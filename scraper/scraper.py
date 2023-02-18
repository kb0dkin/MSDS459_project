# scraper.py
#
# Scrapes data about guitars and reviews from a few different sources,
# then uses that data to populate an EdgeDB instance
#
# Much of the scraper code is just refactoring of Joe's GuitarCenter code, 
# put into a little more organized piece of code


from selenium import webdriver
import time
from bs4 import BeautifulSoup
import os

# local import
import scrape_utils
import class_definitions




# create new instance of firefox driver -- this should be the geckodriver
driver = webdriver.Firefox()

# ---------------------------------------------------
# start with guitarcenter
# ---------------------------------------------------

url_list = [] # 
# iterate over the range of "Nao" values, get links to all guitars
for ii in range(0, 4400, 100):
    html = scrape_utils.gc_get_browsing_pages(driver, ii) # get the html doc

    url_list.append(scrape_utils.gc_extract_links(html)) # append the list of matches

url_list = list(set(url_list)) # get rid of any repeats


# iterate through the urls
for url in url_list:
    # get the entire review set for this page
    html = scrape_utils.gc_get_all_reviews(driver, url)




driver.close()