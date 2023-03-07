# scraper.py
#
# Scrapes data about guitars and reviews from a few different sources,
# then uses that data to populate an EdgeDB instance
#
# Much of the scraper code is just refactoring of Joe's GuitarCenter code, 
# put into a little more organized piece of code


from selenium import webdriver
from selenium.webdriver.firefox.options import Options
# import time
from bs4 import BeautifulSoup
import edgedb
import numpy as np
import json

# local import
import scrape_utils
import class_definitions


# create new instance of firefox driver -- this should be the geckodriver
options = Options()
options.headless = True
options.binary_location = r"C:\\Program Files\\Mozilla Firefox\\firefox.exe"
driver = webdriver.Firefox(executable_path="C:\Program Files\GeckoDriver\geckodriver.exe", options=options)

# ---------------------------------------------------
# start with guitarcenter
# ---------------------------------------------------

url_list = [] #  list of guitar urls
guitars = [] # list of guitars
# iterate over the range of "Nao" values, get links to all guitars
# for ii in range(0, 4400, 100):
for ii in range(0,100,100): # temp testing
    html = scrape_utils.gc_get_browsing_pages(driver, ii) # get the html doc

    url_list.append(scrape_utils.gc_extract_links(html)) # append the list of matches

# make it unique -- also have to flatten it
url_list = list(set([item for sublist in url_list for item in sublist]))

# open an edgedb instance

client = edgedb.create_client(dsn='MSDS_459')

# create a "Guitar Center" vendor and Review Source
client.query(""" INSERT ReviewSource {
                    name := <str>'Guitar Center',
                    sourceType := <default::SourceType>'Vendor',
            } UNLESS CONFLICT """)

# create a "Guitar Center" vendor
client.query(""" INSERT Vendor {
                    name := <str>'Guitar Center',
            } UNLESS CONFLICT """)


# iterate through the urls
# for url in url_list:
# for url_ii, url in enumerate(url_list):
for url in url_list:
    html = scrape_utils.gc_get_all_reviews(driver, url)  
    reviews = scrape_utils.gc_extract_review_info(html) # parse the review info
    guitar = scrape_utils.gc_extract_guitar_info(url, html) # parse the specs for the guitar
    
    try:
        guitar_id = guitar.insert(client) # insert the guitar, get the uuid
    
        for review in reviews:
            review.insert(guitar_id, client)
    
    except:
        print(f'Could not insert guitar {guitar.model}')




# close everything up
driver.close()
client.close()