# from nltk import tokenize
import edgedb

# ---------------------------------------------
# put together a dictionary of valid search terms,
# based on what exists in the database now
# 
# use this as a support function for other scripts
def find_valid_searches() -> dict:
    
    # valid search terms
    search_dict = dict()

    # create a client to search the database
    client = edgedb.create_client(dsn='MSDS_459')

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



# ---------------------------------------------
# parse the request string to look for potential
# expected values
def request_parser(req_raw:str):
    
    # split into individual components
    req_list = req_raw.lower().replace(',','').split()

    # get a list of potential things to match
    template_dict = find_valid_searches()

    # look for matches in the req_list
    req_out = {} # empty dict
    for key,value in template_dict.items():
        # look for any words in the search term that match the 
        matches = [item for item in req_list if item in value]
        if len(matches) != 0:
            req_out[key] = matches

    # asssemble the query string 
    query_str = 'SELECT Guitar {model} filter '
    for key,value in req_out.items():
        query_str = query_str + f" .{key} in {{ {','.join(value)} }}"

    query_str = query_str + ';'

    return query_str


    # tokenize the text
    # entries = tokenize(request)

