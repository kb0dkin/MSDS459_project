from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import re
import class_definitions
import datetime



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


# parse the raw reviews from the html
def gc_extract_review_info(html) -> list :

    # pull out the reviews and separate them into a list
    pattern = r'<div class="pr-rd-star-rating">.*?</p></section>'
    snippets = re.findall(pattern, html, re.DOTALL)
    
    reviews = []
    
    # parse through each review
    for snippet in snippets:
        # normalized review -- to standardize across platforms
        rating = float(re.search(r'Rated (\d+) out of 5 stars', snippet).group(1))/5
        title = re.search(r'id="pr-rd-review-headline-.*?" lang="en">(.*?)<', snippet).group(1)
        author = re.search(r'<p class="pr-rd-details pr-rd-author-nickname">.*?By.*?</span><span>(.*?)</span>', snippet).group(1)
        date = datetime.datetime.fromisoformat(re.search(r'<time datetime="(.*?)">', snippet).group(1))
        text = re.search(r'<p class="pr-rd-description-text" lang="en">(.*?)</p>', snippet)
        if text:
            text = text.group(1)
        else:
            text = ""

        # pros and cons
        pros_list = re.findall(r'Pros</dt>(.*?)</dl>',snippet, re.DOTALL)
        pros_list = [re.findall(r'<dd>(.*?)</dd>', pro) for pro in pros_list]
        pros_list = [item for sublist in pros_list for item in sublist]

        cons_list = re.findall(r'Cons</dt>(.*?)</dl>',snippet, re.DOTALL)
        cons_list = [re.findall(r'<dd>(.*?)</dd>', pro) for pro in cons_list]
        cons_list = [item for sublist in cons_list for item in sublist]

        # best_for 
        best_for_list = re.findall(r'Best for</dt>(.*?)</dl>', snippet, re.DOTALL)
        best_for_list = [re.findall(r'<dd>(.*?)</dd>', best) for best in best_for_list]
        best_for_list = [item for sublist in best_for_list for item in sublist]

        review = class_definitions.Review(rating, title, text, author, date, pros_list, cons_list, best_for_list)
        reviews.append(review)

    # return as a list
    return reviews


def gc_extract_guitar_info(snippets):
