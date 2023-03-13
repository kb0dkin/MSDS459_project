from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import re
import class_definitions
import datetime
import json

## TF stuff
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text

import pandas as pd



# return the html doc for the GC browsing page. 
# driver -- webdriver
# nao_val -- nao value in the address
def gc_get_browsing_pages(driver:webdriver, nao_val:int):

    # assemble the URL
    url = "https://www.guitarcenter.com/Guitars.gc#pageName="\
            "department-page&N=18144+1075&recsPerPage=100&Nao="\
            +str(nao_val)

    driver.get(url) # Navigate to URL
    driver.implicitly_wait(10) # wait for it to load
    time.sleep(3) # pause for 3 seconds
    html = driver.page_source # Extract the html

    return html


# return all links that matche the regular expression r'.%\d{13}\.gc$'
# which is guitar center link format for products
def gc_extract_links(html):
    matches = [] # initialize the set of matches

    soup = BeautifulSoup(html, 'html.parser') # parse the HTML

    # find all the links that match the regexp
    # should we change this to a list comprehension? bit long, but very do-able...
    for link in soup.find_all('a',href=True):
        match = re.search(r'.*\d{13}\.gc$', link['href'])
        if match:
            matches.append(match.group())

    return matches



# repeatedly click the "show more reviews" button until we have all visible
def gc_get_all_reviews(driver:webdriver, url:str):
    driver.get(url) # load the page

    # repeat until we can't
    while True:
        try:
            # scroll to the bottom of the page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            show_more_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".pr-rd-show-more[aria-label='Show More Reviews']"))
            )
            # keep clicking the "Show More Reviews" button until it disappears
            while show_more_button.is_displayed():
                show_more_button.click()
                time.sleep(1)
                show_more_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".pr-rd-show-more[aria-label='Show More Reviews']"))
                )
        except:
            break
    
    return driver.page_source


# parse the raw reviews from the html
def gc_extract_review_info(html) -> list :

    # pull out the reviews and separate them into a list
    # pattern = r'<div class="pr-rd-star-rating">.*?</p></section>' # old pattern - misses pros, cons and best_for
    pattern = r'<div class="pr-rd-star-rating">.*?<div class="pr-rd-helpful-action">'
    snippets = re.findall(pattern, html, re.DOTALL)
    
    reviews = []
    
    # parse through each review
    for snippet in snippets:
        # normalized review -- to standardize across platforms
        rating = float(re.search(r'Rated (\d+) out of 5 stars', snippet).group(1))/5
        title = re.search(r'id="pr-rd-review-headline-.*?" lang="en">(.*?)<', snippet).group(1)
        author = re.search(r'<p class="pr-rd-details pr-rd-author-nickname">.*?By.*?</span><span>(.*?)</span>', snippet).group(1)
        date = datetime.datetime.strptime(re.search(r'<time datetime="(.*?)">', snippet).group(1)[:-5], '%Y-%m-%dT%H:%M:%S').astimezone()
        text = re.search(r'<p class="pr-rd-description-text" lang="en">(.*?)</p>', snippet)
        if text:
            text = text.group(1)
        else:
            text = ""

        review = class_definitions.Review(rating, title, text, author, date)
        reviews.append(review)

    # return as a list
    return reviews


# parse all of the desired spec info for the guitars from the html
def gc_extract_guitar_info(url, html, BERT_model = None) -> class_definitions.Guitar:

    # make and model
    match = re.search(r'[^/]*[^/]', url)
    if match is None:
        manufacturer = None
    else:
        manufacturer = match.group(0)

    # model
    match = re.search(r'"og:title" content="([^"]+)"', html)
    if match is None: 
        match = "" # what is the point of an un-named guitar?
        model = ""
    else:
        model = match.group(1).replace("&nbsp;"," ")
        model = model.replace(manufacturer,'').lstrip() # pop out the manufacturer's name
    
    # get description, which is the string following '"PDPDescription":{"description"'
    match = re.search(r'"PDPDescription":{"description":"([^"]+)"', html)
    if match is None:
        description = ""
    else:
        description = match.group(1)
    description = description_clean(description)
    

    # get features, which is the string following "features"
    # sometimes there are two occurrences, in which case we take the second one (hopefully this works consistently)
    match = re.findall(r'"features":"([^"]+)"', html)
    if len(match)==0:
        features_raw = ""
        feature_list = []
        feature_dict = {}
    else:
        features_raw = match[-1] # if there are two, take the second one
        feature_list = fix_features(extract_strings(features_raw))
        feature_dict = feature_list_to_dict(feature_list) # convert to a dict

    # get specs, which is the string following "specifications"
    match = re.search(r'"specifications":"([^"]+)"', html)
    if match is None:
        specs_raw = ""
    else:
        specs_raw = match.group(1)
    spec_dict = make_spec_dict(fix_specs(extract_strings(specs_raw)))

    # get the type
    guitar_type = 'unknown'
    if (re.search(r'[C|c]lassical',features_raw) is not None) or (re.search(r'[C|c]lassical',model) is not None):
        guitar_type = 'Classical'
    elif (re.search(r'[A|a]coustic[ |-][E|electric]', features_raw) is not None) or (re.search(r'[A|a]coustic [E|electric]', model) is not None):
        guitar_type = 'Acoustic-Electric'
    elif (re.search(r'[A|a]coustic', features_raw) is not None) or (re.search(r'[A|a]coustic', model) is not None):
        guitar_type = 'Acoustic'
    elif (re.search(r'[E|e]lectric', features_raw) is not None) or (re.search(r'[E|e]lectric', model) is not None):
        guitar_type = 'Electric'
    elif (re.search(r'[T|t]ravel', features_raw)  is not None) or (re.search(r'[T|t]ravel', model)  is not None):
        guitar_type = 'Travel'


    # pros and cons
    pros_list = re.findall(r'Pros</dt>(.*?)</dl>',html, re.DOTALL)
    pros_list = [re.findall(r'<dd>(.*?)</dd>', pro) for pro in pros_list]
    pros_list = [item for sublist in pros_list for item in sublist]

    cons_list = re.findall(r'Cons</dt>(.*?)</dl>',html, re.DOTALL)
    cons_list = [re.findall(r'<dd>(.*?)</dd>', con) for con in cons_list]
    cons_list = [item for sublist in cons_list for item in sublist]

    # best_for 
    best_for_list = re.findall(r'Best for</dt>(.*?)</dl>', html, re.DOTALL)
    best_for_list = [re.findall(r'<dd>(.*?)</dd>', best) for best in best_for_list]
    best_for_list = [item for sublist in best_for_list for item in sublist]

    # see if we can fill in the number of strings using a regular expression
    # Note: this is more complicated than it should be, but hidden characters or something was causing problems
    # match = re.search(r"Number of strings:\s*(\d+)", specs_raw) # this should work, but sometimes doesn't
    match = re.search(r"Number of strings:\s*(.{5})", specs_raw, re.IGNORECASE)
    # print(match)
    num_strings = None
    if match is not None:
        match = re.findall(r"\d+", match.group(1))
        if len(match) > 0:
            num_strings = int(match[0])
    else:
        match = re.search(r"Number of strings:\s*(.{5})", features_raw, re.IGNORECASE)
        if match is not None:
            num_strings = int(re.findall(r"\d+", match.group(1))[0])

    # get the body shape (called body type in the specs).  Not 100% reliable at this point.
    match = re.search(r"Body Type:\s*(.{40})", specs_raw, re.ASCII)
    body_shape = "unknown"
    if match is not None:
        match = re.search(r"^\t*(.*?)\\", match.group(1), re.ASCII)
        if match is not None:
            body_shape = match.group(1)

    # num_frets
    match = re.search(r"Number of frets:\s*(.{5})", specs_raw, re.IGNORECASE)
    num_frets = None
    if match is not None:
        match = re.findall(r"\d+", match.group(1))
        if len(match) > 0:
            num_frets = int(match[0])

    # scale_length
    match = re.search(r"Scale length:\s*(.{7})", specs_raw, re.IGNORECASE)
    scale_length = None
    if match is not None:
        match = re.findall(r"\d*\.\d+", match.group(1))
        if len(match) > 0:
            scale_length = float(match[0])

    # url
    url_full = "https://www.guitarcenter.com" + url

    # add in the embedding if it's available
    if BERT_model is not None:
        embedding = json.dumps(BERT_model.predict([description], verbose=0)['encoder_outputs'][0].tolist())
    else:
        embedding = []


    guitar = class_definitions.Guitar(model=model, description=description, features=feature_list,\
                                      guitar_type=guitar_type, manufacturer=manufacturer, url=url_full,\
                                      num_strings=num_strings, body_shape=body_shape, num_frets=num_frets,\
                                      scale_length=scale_length, embedding=embedding)

    # guitar = feat_dict_into_guitar(guitar=guitar, feat_dict=feature_dict) # redundant?  Need to discuss!



    return guitar




# Reads the strings between the specified tags
def extract_strings(str):
    str = str.replace("\\\\", "\\")
    extracted_string = re.findall(r'li\\u003e(.*?)\\u003c/li', str)
    return extracted_string

# Fixes anomalies in the features strings
def fix_features(str_list):
    for i in range(len(str_list)):
        str_list[i] = str_list[i].replace("\\t", " ")
        str_list[i] = str_list[i].replace("\\n", " ")
        # Remove any space at beginning or end of each string
        str_list[i] = str_list[i].strip()
    return str_list

# split features into a dictionary to allow for easy loading into the guitar class
def feature_list_to_dict(feat_list:list) -> dict:
    # iterate through list, create a dict
    feat_dict = {item.split(': ')[0]:item.split(': ')[1] for item in feat_list if len(item.split(': ')) == 2}
    return feat_dict

# Gets the specs from the specs string
def fix_specs(str_list):
    # Remove any space at beginning or end of each string
    # Remove any of the following: "\\u0026amp; ", "\\u0026quot;", "\u0026nbsp;", "\t", "\n"
    for i in range(len(str_list)):
        str_list[i] = str_list[i].replace("\\u0026amp; ", "")
        str_list[i] = str_list[i].replace("\\u0026quot;", "")
        str_list[i] = str_list[i].replace("\\u0026nbsp;", "")
        str_list[i] = str_list[i].replace("\\t", " ")
        str_list[i] = str_list[i].replace("\\n", " ")
        str_list[i] = str_list[i].strip()
    return str_list

# Makes a dictionary from the list of strings
def make_spec_dict(str_list):
    # Make a dictionary by taking whatever is before the colon as the key and whatever is after as the value
    spec_dict = {}
    for i in range(len(str_list)):
        colon_pos = str_list[i].find(":")
        key = str_list[i][:colon_pos]
        value = str_list[i][colon_pos+2:] # +2 instead of +1 to skip the space after the colon
        spec_dict[key] = value
    return spec_dict

# clean up junk from the description
def description_clean(description:str) -> str:
    replace_list = ["\\u003cstyle",\
                    "\\u003c/style",\
                    "\\u003cbr",\
                    "\\u003e",\
                    "\\u0026nbsp",\
                    " /",\
                    "\\u003cp",\
                    "\\u003c",\
                    "div id=\\",\
                    "style\\u003e ",\
                    "/p","'","\\"]
    
    for item in replace_list:
        description = description.replace(item, "")
    
    return description


# get rid of non-numeric characters, return an int (for fret num, string num etc)
def strip_alpha(base_str:str) -> int:
    return re.sub('[^0-9]','',base_str)

def feat_dict_into_guitar(guitar:class_definitions.Guitar,feat_dict:dict) -> class_definitions.Guitar:

    for key,value in feat_dict.items():
        if key == 'Body type':
            guitar.body_shape = value
        if key == 'Cutaway':
            guitar.cutaway = value
        if key == 'Pickup/preamp':
            guitar.pickups = value
        if key == 'Number of frets':
            guitar.num_frets = strip_alpha(value)
        if key == 'Number of strings':
            guitar.num_strings = strip_alpha(value)
        if key == 'Scale length':
            guitar.scale_length = strip_alpha(value)
    
    return guitar

def printGuitar(guitar):
    print("Model: " + guitar.model)
    print("Description: " + guitar.description)
    print("Features: " + str(guitar.features))
    print("Guitar type: " + guitar.guitar_type)
    print("Manufacturer: " + guitar.manufacturer)
    print("URL: " + guitar.url)
    print("Number of strings: " + str(guitar.num_strings))
    print("Body shape: " + guitar.body_shape)
    print("Number of frets: " + str(guitar.num_frets))
    # print("Pickups: " + guitar.pickups)
    print("Scale length: " + str(guitar.scale_length))
    # print("Cutaway: " + guitar.cutaway)
    print("Pros: " + str(guitar.pros))
    print("Cons: " + str(guitar.cons))
    print("Best for: " + str(guitar.best_for))
    input("Press Enter to continue...")
    print("")


# ---------------------------------------------------------------------
# Embedding the description in a pretrained BERT model
# 
#    This is for both the initial embeddings and the request, so it's 
#    a helper function for those two
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
    

