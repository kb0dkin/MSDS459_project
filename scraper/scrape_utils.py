from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import re



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
    matches = [] # initialize the list of matches

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