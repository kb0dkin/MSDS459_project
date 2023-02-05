# Extracts product page links from the HTML files saved by save_product_pages.py.

import re
from bs4 import BeautifulSoup

matches = []

# Iterate over the browsing pages
for i in range(0, 4400, 100):
    # Open the HTML file
    with open(f"guitarcenter_{i}.html", "r") as file:
        html = file.read()

    # Parse the HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Find all links that match the regular expression
    for link in soup.find_all('a', href=True):
        match = re.search(r'.*\d{13}\.gc$', link['href'])
        if match:
            matches.append(match.group())

# Print the matches
print(matches)

# get unique matches
matches_unique = list(set(matches))

# save the matches to a file
with open("product_urls.txt", "w") as file:
    file.write("\n".join(matches_unique))

