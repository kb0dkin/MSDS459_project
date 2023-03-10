import edgedb

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
    query_str = 'SELECT Guitar {model, description} filter '
    delim_str = "', '"
    for key,value in req_out.items():
        query_str = query_str + f" .{key} in {{ \'{delim_str.join(value)}\' }}"

    # now look for manufacturers
    manus = find_manufacturers(client)
    manu_matches = [item for item in manus if str(item).lower() in req_list]
    if len(manu_matches) > 0:
        query_str = query_str + f'.brand.name in {{ \'{delim_str.join(manu_matches)}\' }}'

    query_str = query_str + ' limit 5;'

    return query_str

