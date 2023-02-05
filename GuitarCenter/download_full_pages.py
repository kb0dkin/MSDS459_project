# Downloads the full HTML of each product page.  Selenium is used to scroll to the bottom of the page to load all the reviews.

import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


saveDir = "product_pages_full"

# set up webdriver
driver = webdriver.Chrome()

# read in the product URLs
with open("product_urls.txt", "r") as file:
    urls = file.read().splitlines()

# Iterate over the product URLs
# for i in range(0,4500):
#
#     # Construct the full URL
#     url_partial = urls[i]
    url_partial = "/Charvel/Pro-Mod-San-Dimas-Style-1-2H-FR-Electric-Guitar-Matte-Blue-Frost-1500000183812.gc"; i=0
    print(f"{i}: {url_partial}")
    url = "https://www.guitarcenter.com" + url_partial
    driver.get(url)

    # click on "Show More Reviews" button and wait
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

    # get HTML
    html = driver.page_source

    # Save the HTML to a file.
    # Everything before the slash is the directory, everything after except the ".gc" is the file name.
    # If the subdirectory doesn't exist, create it.
    subDir = url_partial[1:url_partial.rfind('/')]
    if not os.path.exists(f"{saveDir}/{subDir}"):
        os.makedirs(f"{saveDir}/{subDir}")
    with open(f"{saveDir}/{url_partial[1:-3]}.html", "w", encoding='utf-8') as file:
        file.write(html)
