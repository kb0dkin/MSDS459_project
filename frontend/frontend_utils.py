import edgedb
import random
import numpy as np
import json

## TF stuff
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text


# ---------------------------------------------
# put together a dictionary of valid search terms,
# based on what exists in the database now
# 
# use this as a support function for other scripts
def find_valid_searches(client) -> dict:
    
    # valid search terms
    search_dict = dict()

    # find valid entries for all "string" fields
    str_props = ['body_shape','cutaway','pickups', 'type', 'country_of_origin']
    for prop in str_props:
        query_string = f'''WITH prop :=
                (SELECT Guitar.{prop} filter Guitar.{prop} != '')
                SELECT DISTINCT prop'''
        search_dict[prop] = client.query(query_string)
    
    # find all entries for all numeric fields
    num_props = ['num_strings','scale_length','num_frets']
    for prop in num_props:
        query_string = f'''WITH prop :=
                (SELECT Guitar.{prop} filter Guitar.{prop} != 0)
                SELECT DISTINCT prop'''
        search_dict[prop] = client.query(query_string)

    # return it
    return search_dict

def find_manufacturers(client) -> list:

    # get all the unique manufacturer names 
    query_string = ''' WITH manufacturers := (
                            SELECT Manufacturer.name
                            )
                        SELECT DISTINCT manufacturers;
    '''

    # flatten the list as necessary. Should just be a list of strings
    manufacturers = [item for item in client.query(query_string)]
    return manufacturers

# ---------------------------------------------
# parse the request string to look for potential
# expected values
def request_parser(req_raw:str):
    
    # create a client to search the database
    client = edgedb.create_client(dsn='MSDS_459')

    # split into individual components
    req_list = req_raw.lower().replace(',','').split()

    # get a list of potential things to match
    template_dict = find_valid_searches(client)

    # look for properties that match
    req_out = {} # empty dict
    for key,value in template_dict.items():
        matches = [item for item in value if str(item).lower() in req_list]
        if len(matches) != 0:
            req_out[key] = matches

    # asssemble the query string 
    query_str = 'SELECT Guitar {model, description, brand: {name}, num_strings, type, cutaway, num_frets, scale_length} '
    delim_str = "', '"
    filter_count = 0
    for key,value in req_out.items():
        if filter_count == 0: # add the filter term -- this allows us to return something random if nothing matches
            query_str += "filter "
            filter_count += 1

        else: # add and AND if we have multiple filters
            query_str = query_str + " AND "

        query_str = query_str + f" .{key} in {{ \'{delim_str.join(value)}\' }} "
        


    # now look for manufacturers
    manus = find_manufacturers(client)
    manu_matches = [item for item in manus if str(item).lower() in req_list]
    if len(manu_matches) > 0:
        if filter_count == 0: # add the filter term -- this allows us to return something random if nothing matches
            query_str += "filter "
            filter_count += 1

        else: # add and AND if we have multiple filters
            query_str = query_str + " AND "

        query_str = query_str + f'.brand.name in {{ \'{delim_str.join(manu_matches)}\' }} '

    query_str = query_str + ' limit 5;'

    return query_str


# ----------------------------------------------------
# Collecting and parsing data for plotting
#
# To fascilitate plotting etc, we'll take care of working with
# edgedb back here, then just let the app handle the bokeh side 
# of things
def plot_data_grabber():
    # initialize a client to connect to edgedb
    client = edgedb.create_client('MSDS_459')

    query_str = '''with gt := (GROUP Guitar {model} by .type)
                    select gt {gguitars := .elements.model,
                                guitar_type := .key.type};'''
    type_grouping = client.query(query_str)

    type_dict = {}
    for guitar_type in type_grouping:
        type_dict[guitar_type['guitar_type']] = guitar_type['gguitars']

    return type_dict


# -----------------------------------------------------
# Import the BERT TF model, to allow for embeddings
def BERT_embed_model():
    # let's start with small bert, just to make it a little more manageable
    bert_handle = 'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-512_A-8/1'
    prep_handle = 'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3'

    # turn text into a tensor
    text_input = tf.keras.layers.Input(shape=(), dtype=tf.string, name='text')

    prep_layer = hub.KerasLayer(prep_handle) # initially vectorize text
    encoder_inputs = prep_layer(text_input) # define prep to encoder flow
    encoder = hub.KerasLayer(bert_handle) # encoder (BERT) model
    outputs = encoder(encoder_inputs) # flow through the model
    # net = outputs['pooled output'] # what we 

    return tf.keras.Model(text_input, outputs)


# -----------------------------------------------------
# Embed the request, and look for the five closest description embeddings
def NLP_Guitar_Finder(req:str):
    BERT_model = BERT_embed_model()
    embedding = BERT_model.predict([req])['encoder_outputs'][0]

    # to make this work more quickly, we will find the 
    # total number of guitars available and just take
    # a random subset of 200
    with edgedb.create_client('MSDS_459') as client:
        # randomly choose an offset
        num_gs = client.query('SELECT count(Guitar);')[0]
        offset_gs = random.randint(0,num_gs-201)
        
        # Get a random subset of embeddings
        embeds = client.query(f'SELECT Guitar {{ embedding, id }} OFFSET {offset_gs} limit 200;')
        dist = np.ndarray([200,])    
        for i_embed, embed in enumerate(embeds):
            # convert embedding from json to numpy, then calculate the l2 
            # (aka Distance)
            dist[i_embed] = np.linalg.norm(np.array(json.loads(embed.embedding))-embedding)

        closest_inds = np.argsort(dist)[0:5] # get the five closest

        # create the query. I'm sure I could use arrays here.
        sql_query = '''SELECT Guitar { model, brand: {name}, description, num_strings, num_frets, cutaway, scale_length}
                        FILTER .id in 
                        {  <uuid>$id0, <uuid>$id1, <uuid>$id2, <uuid>$id3, <uuid>$id4}'''
        guitars = client.query(sql_query,\
                            id0=embeds[closest_inds[0]].id,\
                            id1=embeds[closest_inds[1]].id,\
                            id2=embeds[closest_inds[2]].id,\
                            id3=embeds[closest_inds[3]].id,\
                            id4=embeds[closest_inds[4]].id )
        
        return guitars
        

# ----------------------------------------------------------
# Results Parser
#   Turning a series of nested Edgedb objects into dictionaries
def Guitar_results_parser(guitars:list):

    guitars_dict = {} # empty dict to store all of the guitars
    for guitar in guitars: # iterate through the guitars
        temp_dict = {} # dict per guitar
        for key in dir(guitar): # iterate through properties
            if key in ['model','id']: # ignore model and id
               continue 
            elif key == 'brand': # brand is different since it's a link
                temp_dict[key] = guitar.brand.name
            else: # make sure it isn't empty
                attr = getattr(guitar, key)
                if (attr != 0) and (attr != ''):
                    temp_dict[key] = attr
        
        # put it all into the guitar_dict
        guitars_dict[guitar.model] = temp_dict


    return guitars_dict # send it home
                
        



