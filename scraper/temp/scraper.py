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
import os

# local import
import scrape_utils
import class_definitions

have_urls = True
have_pages = False
saveDir = "../product_pages_full" # for the html files

# create new instance of firefox driver -- this should be the geckodriver
options = Options()
options.headless = True
options.binary_location = r"C:\\Program Files\\Mozilla Firefox\\firefox.exe"
driver = webdriver.Firefox(executable_path="C:\Program Files\GeckoDriver\geckodriver.exe", options=options)
# driver = webdriver.Chrome()

# ---------------------------------------------------
# start with guitarcenter
# ---------------------------------------------------

# get the list of urls (if we don't have it already)
if have_urls:
    # read the urls from the file
    with open("product_urls.txt", "r") as file:
        url_list = file.read().splitlines()

else:
    url_list = [] #  list of guitar urls
    # iterate over the range of "Nao" values, get links to all guitars
    print("Scraping list of all Guitar Center URLs")
    for ii in range(0,4400,100):
        print('.',end='')
        html = scrape_utils.gc_get_browsing_pages(driver, ii) # get the html doc

        url_list.append(scrape_utils.gc_extract_links(html)) # append the list of matches

    # make it unique -- also have to flatten it
    url_list = list(set([item for sublist in url_list for item in sublist]))

    # save the matches to a file
    with open("product_urls.txt", "w") as file:
        file.write("\n".join(url_list))


# get the individual guitar pages (if we don't have them already)
if not have_pages:
    print("Downloading HTML pages for all Guitar Center URLs.")
    n_urls = len(url_list)
    for i in range(123, n_urls): # can modify this to only download a subset of the urls at a time
        # Construct the full URL
        url_partial = url_list[i]
        print(f"{i}: {url_partial}")
        url = "https://www.guitarcenter.com" + url_partial
        driver.get(url)
        html = scrape_utils.gc_get_all_reviews(driver, url)

        # Save the HTML to a file.
        # Everything before the slash is the directory, everything after except the ".gc" is the file name.
        # If the subdirectory doesn't exist, create it.
        subDir = url_partial[1:url_partial.rfind('/')]
        if not os.path.exists(f"{saveDir}/{subDir}"):
            os.makedirs(f"{saveDir}/{subDir}")
        with open(f"{saveDir}/{url_partial[1:-3]}.html", "w", encoding='utf-8') as file:
            file.write(html)


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
print("Scraping individual guitars")
# n_urls = len(url_list)
# for i in range(0, n_urls): # can modify this while debugging
    # load from file
    # url = url_list[i]
for url in url_list:
    with open(f"{saveDir}/{url[1:-3]}.html", "r", encoding='utf-8') as file:
        html = file.read()
    reviews = scrape_utils.gc_extract_review_info(html) # parse the review info
    guitar = scrape_utils.gc_extract_guitar_info(url, html) # parse the specs for the guitar
    print(guitar.scale_length)

    try:
        guitar_id = guitar.insert(client) # insert the guitar, get the uuid

        for review in reviews:
            review.insert(guitar_id, client)

    except:
        print(f'Could not insert guitar {guitar.model}')




# close everything up
driver.close()
client.close()
