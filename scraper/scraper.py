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
from os import path

# local import
import scrape_utils
import class_definitions

have_urls = True # changed this to just check if the file exists
have_pages = True
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
url_file = 'product_urls.txt'
if path.exists(url_file):
    # read the urls from the file
    with open(url_file, "r") as file:
        url_list = file.read().splitlines()
    print(f'List of Guitars and URLs read from {url_file}')

else:
    url_list = [] #  list of guitar urls
    # iterate over the range of "Nao" values, get links to all guitars
    print("Scraping list of all Guitar Center Guitars")
    for ii in range(0,4400,100):
        print('.',end='')
        html = scrape_utils.gc_get_browsing_pages(driver, ii) # get the html doc

        url_list.append(scrape_utils.gc_extract_links(html)) # append the list of matches

    # make it unique -- also have to flatten it
    url_list = list(set([item for sublist in url_list for item in sublist]))

    # save the matches to a file
    with open(url_file, "w") as file:
        file.write("\n".join(url_list))
    
    print(f'\nList of Guitars and URLs written to {url_file}')


# urls to use for scraping and inserting into the db.
n_urls = len(url_list)
scrape_start = n_urls-100 # should probably make this changeable from the command line 
scrape_end = n_urls
len_scrape = scrape_end-scrape_start

# get the individual guitar pages (if we don't have them already)
if not have_pages:
    
    print(f"Downloading HTML pages for {len_scrape} Guitar Center URLs.")
    status_steps = np.ceil(len_scrape/20)
    for i_url in range(scrape_start, scrape_end): # can modify this to only download a subset of the urls at a time

        # a nice little status bar :)
        curr_status = int(np.ceil(i_url/status_steps))
        print(f"[{curr_status*'-'}{(20-curr_status)*' '}]   {url_partial}",end='\r')    

        # Construct the full URL
        url_partial = url_list[i_url]
        save_name = f"{saveDir}{path.splitext(url_partial)[0]}.html"
        if not path.exists(save_name):
            url = "https://www.guitarcenter.com" + url_partial
            driver.get(url)
            html = scrape_utils.gc_get_all_reviews(driver, url)

            # create a directory as needed
            subDir = path.split(url_partial)[0]
            if not path.exists(saveDir + subDir):
                os.makedirs(f"{saveDir}{subDir}")
            with open(save_name, "w", encoding='utf-8') as file:
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
print("Adding guitars to the database")
for url in url_list:

    # check to make sure that we have scraped the html
    url_file = f"{saveDir}/{url[1:-3]}.html"
    if path.exists(url_file):
        with open(url_file, "r", encoding='utf-8') as file:
            html = file.read()

        reviews = scrape_utils.gc_extract_review_info(html) # parse the review info
        guitar = scrape_utils.gc_extract_guitar_info(url, html) # parse the specs for the guitar
        # print(guitar.scale_length)

        if len(client.query(f"SELECT Guitar filter .model = <str>$model", model=guitar.model)):
            try:
                guitar_id = guitar.insert(client) # insert the guitar, get the uuid

                for review in reviews:
                    review.insert(guitar_id, client)

            except:
                print(f'Could not insert guitar {guitar.model}')

    else:
        print(f"{url_file} has not been downloaded")




# close everything up
driver.close()
client.close()
