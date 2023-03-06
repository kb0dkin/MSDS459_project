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

url_list = np.unique(url_list).tolist() # get rid of any repeats

# open an edgedb instance

client = edgedb.create_client(dsn='MSDS_459')

# iterate through the urls
# for url in url_list:
for url_ii, url in enumerate(url_list):
    html = scrape_utils.gc_get_all_reviews(driver, url)  
    reviews = scrape_utils.gc_extract_review_info(html) # parse the review info
    guitar = scrape_utils.gc_extract_guitar_info(url, html) # parse the specs for the guitar

    
    # *todo* -- enable entity linking!        
    g_id = client.query("""
        INSERT Guitar {
            model := <str>$model,
            type := <str>$g_type,
            body_shape := <str>$body_shape,
            cutaway := <str>$cutaway,
            num_strings := <int32>$num_strings,
            scale_length := <float64>$scale_length,
            num_frets := <int32>$num_frets,
            description := $description
        }
    """, model=guitar.model, body_shape = guitar.body_shape, cutaway = guitar.cutaway,\
        num_strings = guitar.num_strings, scale_length = guitar.scale_length,\
        num_frets = guitar.num_frets, description = guitar.description, g_type = "guitar")
    
    # Review insertions
    for review in reviews:
        review_set = client.query("""
            INSERT Review {
                normalized_rating:= <float64>$rating,
                date:= <std::datetime>$date,
                pros := <array<str>>$pros,
                cons := <array<str>>$cons,
                best_for := <array<str>>$best_for,
                guitar := $guitar,
                written_review -> $text,
            }
        """,\
            rating=review.rating, date=review.date,\
            pros=review.pros, cons=review.cons,\
            best_for= review.best_for, guitar=g_id,\
            text = review.text)
        
        author_set = client.query("""
            SELECT Reviewer FILTER Reviewer.review.id = $review_id
        """, review_id = review_set[0])
        
        
    




driver.close()
client.close()