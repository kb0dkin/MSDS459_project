# Gets the browsing pages (100 guitars per page) and saves them to files.

from selenium import webdriver
import time
from bs4 import BeautifulSoup
import os

saveDir = "blah"

# Create a new instance of the Firefox driver
driver = webdriver.Firefox()

# create the directory if it doesn't exist
if not os.path.exists(saveDir):
    os.makedirs(saveDir)

# Define the base URL
base_url = "https://www.guitarcenter.com/Guitars.gc#pageName=department-page&N=18144+1075&recsPerPage=100&Nao="

# Iterate over the range of Nao values
for i in range(0, 4400, 100):
    # Construct the full URL
    url = base_url + str(i)

    # Navigate to the URL
    driver.get(url)

    # Wait for the content to load
    driver.implicitly_wait(10)

    # Pause for 3 seconds
    time.sleep(3)

    # Extract the HTML
    html = driver.page_source

    # Save the HTML to a file
    with open(f"{saveDir}/guitarcenter_{i}.html", "w", encoding='utf-8') as file:
        file.write(html)

# Close the browser
driver.close()