# Extracts

import os
import re

# Where the HTML files are saved
saveDir = "product_pages_full"

# Make a Review class that has attributes "name", "location", "title", "text", "rating", "pros", "cons" and "best_for"
class Review:
    def __init__(self, rating, title, text):
        self.rating = rating
        self.title = title
        self.text = text

    def __str__(self):
        return f"{self.rating}, {self.title}, {self.text}"

# Make a Guitar class that has attributes "model", "rating", "num_ratings", "price", "description", "item_num", "pos_num",
# "features", "specs", "warranty", "reviews" and "url"
class Guitar:
    def __init__(self, model, rating, num_ratings, price, description, item_num, pos_num, features, specs, reviews, pros, cons, best_for, makeAndModelStr):
        self.model = model #
        self.rating = rating #
        self.num_ratings = num_ratings #
        self.price = price #
        self.description = description #
        self.item_num = item_num #
        self.pos_num = pos_num #
        self.features = features #
        self.specs = specs #
        self.reviews = reviews #
        self.pros = pros #
        self.cons = cons #
        self.best_for = best_for #
        self.url = makeAndModelStr #

    def __str__(self):
        return f"{self.model}, {self.rating}, {self.num_reviews}, {self.price}, {self.description}, {self.item_num}, {self.pos_num}, {self.features}, {self.specs}, {self.warranty}, {self.reviews}, {self.url}"

# Reads the strings between the specified tags
def extract_strings(str):
    str = str.replace("\\\\", "\\")
    extracted_string = re.findall(r'li\\u003e(.*?)\\u003c/li', str)
    return extracted_string

# Fixes anomalies in the features strings
def fix_features(str_list):
    for i in range(len(str_list)):
        str_list[i] = str_list[i].replace("\\t", " ")
        str_list[i] = str_list[i].replace("\\n", " ")
        # Remove any space at beginning or end of each string
        str_list[i] = str_list[i].strip()
    return str_list

# Gets the specs from the specs string
def fix_specs(str_list):
    # Remove any space at beginning or end of each string
    # Remove any of the following: "\\u0026amp; ", "\\u0026quot;", "\u0026nbsp;", "\t", "\n"
    for i in range(len(str_list)):
        str_list[i] = str_list[i].replace("\\u0026amp; ", "")
        str_list[i] = str_list[i].replace("\\u0026quot;", "")
        str_list[i] = str_list[i].replace("\\u0026nbsp;", "")
        str_list[i] = str_list[i].replace("\\t", " ")
        str_list[i] = str_list[i].replace("\\n", " ")
        str_list[i] = str_list[i].strip()
    return str_list

# Makes a dictionary from the list of strings
def make_spec_dict(str_list):
    # Make a dictionary by taking whatever is before the colon as the key and whatever is after as the value
    spec_dict = {}
    for i in range(len(str_list)):
        colon_pos = str_list[i].find(":")
        key = str_list[i][:colon_pos]
        value = str_list[i][colon_pos+2:] # +2 instead of +1 to skip the space after the colon
        spec_dict[key] = value
    return spec_dict

# Gets the review HTML snippets
def extract_review_snippets(str):
    pattern = r'<div class="pr-rd-star-rating">.*?</p></section>'
    snippets = re.findall(pattern, str, re.DOTALL)
    return snippets

# def extract_review_snippets(str, pos=0):
#     pattern = r'<div class="pr-rd-star-rating">.*?</p></section>'
#     snippets = list(re.finditer(pattern, str[pos:], re.DOTALL))
#     end_pos = (snippets[-1].end() + pos) if snippets else pos
#     return snippets, end_pos

# Processes the review HTML snippets
def process_snippets(snippets):
    reviews = []
    for snippet in snippets:
        # rating is the number following "Rated ", careful to avoid error "'str' object has no attribute 'group'"
        rating = re.search(r'Rated (\d+) out of 5 stars', snippet).group(1)
        # title is string between > and < following "id="pr-rd-review-headline-XXXXXXXXX" lang="en""
        title = re.search(r'id="pr-rd-review-headline-.*?" lang="en">(.*?)<', snippet).group(1)
        # review is between <p class="pr-rd-description-text" lang="en"> and </p>
        text = re.search(r'<p class="pr-rd-description-text" lang="en">(.*?)</p>', snippet)
        if text:
            text = text.group(1)
        else:
            text = ""
        # review = re.search(r'.*<p class="pr-rd-description-text" lang="en">(.*?)</p>.*', snippet).group(1)
        # review = re.search(re.compile(r'<p class="pr-rd-description-text" lang="en">(.*?)</p>'), snippet).group(1)

        # regex = re.compile(r'<p class="pr-rd-description-text" lang="en">(.*?)</p>')
        # review = regex.search(snippet)

        # print rating and title
        print(f"Rating: {rating}, Title: {title}")
        # print the review
        print(f"Review: {text}")
        review = Review(rating, title, text)
        reviews.append(review)

    return reviews

def extract_pros(html):
    # Extract the list of strings between "Pros</dt>" and "</dl>"
    pros_list = re.findall(r'Pros</dt>(.*?)</dl>', html, re.DOTALL)
    if pros_list:
        # Extract the list of strings between "<dd>" and "</dd>"
        pros_list = [re.findall(r'<dd>(.*?)</dd>', review) for review in pros_list]
    else:
        pros_list = []
    # Convert the list of lists into a list of strings
    pros_list = [item for sublist in pros_list for item in sublist]
    # print the list of pros
    print(f"Pros: {pros_list}")
    return pros_list

def extract_cons(html):
    # Extract the list of strings between "Cons</dt>" and "</dl>"
    cons_list = re.findall(r'Cons</dt>(.*?)</dl>', html, re.DOTALL)
    if cons_list:
        # Extract the list of strings between "<dd>" and "</dd>"
        cons_list = [re.findall(r'<dd>(.*?)</dd>', review) for review in cons_list]
    else:
        cons_list = []
    # Convert the list of lists into a list of strings
    cons_list = [item for sublist in cons_list for item in sublist]
    # print the list of cons
    print(f"Cons: {cons_list}")
    return cons_list

def extract_best_for(html):
    # Extract the list of strings between "Best for</dt>" and "</dl>"
    best_for_list = re.findall(r'Best for</dt>(.*?)</dl>', html, re.DOTALL)
    if best_for_list:
        # Extract the list of strings between "<dd>" and "</dd>"
        best_for_list = [re.findall(r'<dd>(.*?)</dd>', review) for review in best_for_list]
    else:
        best_for_list = []
    # Convert the list of lists into a list of strings
    best_for_list = [item for sublist in best_for_list for item in sublist]
    # print the list of best for
    print(f"Best for: {best_for_list}")
    return best_for_list



# Start a list of guitars
guitars = []

# If file "raw_strings.txt" exists, delete it
if os.path.exists("raw_strings.txt"):
    os.remove("raw_strings.txt")

# If file "guitarcenter.json" exists, delete it
if os.path.exists("guitarcenter.json"):
    os.remove("guitarcenter.json")

# Loop through all files in the saveDir
for subdir, dirs, files in os.walk(saveDir):

    # Loop through all files within each subdirectory
    for fileStr in files:
        makeAndModelStr = subdir[subdir.rfind("\\")+1:] + f"/{fileStr[:-5]}" # also is folder path and partial URL
        print(makeAndModelStr) # print the subdir and file name
        # open the file
        with open(f"{subdir}/{fileStr}", "r", encoding='utf-8') as file:
            # read the file
            html = file.read()
            # get reviews using a helper function
            review_snippets = extract_review_snippets(html)
            reviews = process_snippets(review_snippets)
            print(f"Number of reviews: {len(review_snippets)}")
            # get pros using a helper function
            pros = extract_pros(html)
            # get cons using a helper function
            cons = extract_cons(html)
            # get best for using a helper function
            best_for = extract_best_for(html)
            # get item_num
            match = re.search(r'"id":"([^"]+)"', html)
            if match is None:
                item_num = ""
                print("item_num not found")
            else:
                item_num = match.group(1)
                pos = match.end()
                print(f"item_num: {item_num} ({pos})")
            # get pos_num, which is the string following "postId"
            match = re.search(r'"postId":"([^"]+)"', html[pos:])
            if match is None:
                pos_num = ""
                print("pos_num not found")
            else:
                pos_num = match.group(1)
                pos += match.end()
                print(f"pos_num: {pos_num} ({pos})")
            # get rating, which is the string following "overallRating"
            match = re.search(r'"overallRating":"([^"]+)"', html[pos:])
            if match is None:
                rating = ""
                print("rating not found")
            else:
                rating = match.group(1)
                pos += match.end()
                print(f"rating: {rating} ({pos})")
            # get num_ratings, which is the string following "ratingCount"
            match = re.search(r'"ratingCount":"([^"]+)"', html[pos:])
            if match is None:
                num_ratings = ""
                print("num_ratings not found")
            else:
                num_ratings = match.group(1)
                pos += match.end()
                print(f"num_ratings: {num_ratings} ({pos})")
            # get model, which is the string following "title"
            match = re.search(r'"title":"([^"]+)"', html[pos:])
            if match is None:
                model = ""
                print("model not found")
            else:
                model = match.group(1)
                pos += match.end()
                print(f"model: {model} ({pos})")
            # get description, which is the string following '"PDPDescription":{"description"'
            match = re.search(r'"PDPDescription":{"description":"([^"]+)"', html[pos:])
            if match is None:
                description = ""
                print("description not found")
            else:
                description = match.group(1)
                pos += match.end()
                print(f"description: {description} ({pos})")
            # get features, which is the string following "features"
            match = re.search(r'"features":"([^"]+)"', html[pos:])
            if match is None:
                features_raw = ""
                print("features not found")
            else:
                features_raw = match.group(1)
                pos += match.end()
                print(f"features: {features_raw} ({pos})")
            feature_list = fix_features(extract_strings(features_raw))
            # get specs, which is the string following "specifications"
            match = re.search(r'"specifications":"([^"]+)"', html[pos:])
            if match is None:
                specs_raw = ""
                print("specs not found")
            else:
                specs_raw = match.group(1)
                pos += match.end()
                print(f"specs: {specs_raw} ({pos})")
            spec_dict = make_spec_dict(fix_specs(extract_strings(specs_raw)))
            # get price, which is the string following "salePrice"
            match = re.search(r'"salePrice":"([^"]+)"', html[pos:])
            if match is None:
                price = ""
                print("price not found")
            else:
                price = match.group(1)
                pos += match.end()
                print(f"price: {price} ({pos})")

            # save makeAndModelStr, features_raw, and specs_raw to raw_strings.csv, followed by a newline
            with open("raw_strings.txt", "a", encoding='utf-8') as file:
                file.write(f"{makeAndModelStr}\n")
                file.write(f"{features_raw}\n")
                # store elements of feature_list as a bullet point list
                for feature in feature_list:
                    file.write(f"* {feature}\n")
                file.write(f"{specs_raw}\n")
                # store elements of spec_dict as a bullet point list
                for key, value in spec_dict.items():
                    file.write(f"* {key}: {value}\n")
                file.write("\n")


            # remove any of the following strings from description:
            #   "\u003cstyle", "\u003c/style", "\u003cbr", "\u003e", "\u0026nbsp", " /", "\u003cp", "\u003c", "div id=\", "style\u003e ", "/p"
            description = description.replace("\\u003cstyle", "")
            description = description.replace("\\u003c/style", "")
            description = description.replace("\\u003cbr", "")
            description = description.replace("\\u003e", "")
            description = description.replace("\\u0026nbsp", "")
            description = description.replace(" /", " ")
            description = description.replace("\\u003cp", "")
            description = description.replace("\\u003c", "")
            description = description.replace("div id=\\", "")
            description = description.replace("style\\u003e ", "")
            description = description.replace("/p", "")

            # Prints extracted feature_list and spec_dict
            print(feature_list)
            print(spec_dict)

            # Save extracted data to json file, with the object name being the makeAndModelStr
            with open("guitarcenter.json", "a", encoding='utf-8') as file:
                file.write(f"\"{makeAndModelStr}\": {{\n")
                file.write(f"\"model\": \"{model}\",\n")
                file.write(f"\"pos_num\": \"{pos_num}\",\n")
                file.write(f"\"price\": \"{price}\",\n")
                file.write(f"\"rating\": \"{rating}\",\n")
                file.write(f"\"num_ratings\": \"{num_ratings}\",\n")
                file.write(f"\"description\": \"{description}\",\n")
                file.write(f"\"features\": \"{feature_list}\",\n")
                file.write(f"\"specs\": \"{spec_dict}\",\n")
                file.write(f"\"pros\": \"{pros}\",\n")
                file.write(f"\"cons\": \"{cons}\",\n")
                file.write(f"\"best_for\": \"{best_for}\",\n")
                file.write("},\n")


            input("Press Enter to continue...")


# read in file guitarcenter.json and store the data to a dictionary called blah
with open("guitarcenter.json", "r", encoding='utf-8') as file:
    blah = json.load(file)
    

# def extract_strings(str):
#     str = str.replace("\\\\", "\\")
#     extracted_string = re.findall(r'li\\u003e(.*?)\\u003c/li', str)
#     return extracted_string
#
# example_string = '\u003cul\u003e\u003cli\u003eSolid European spruce top with myrtlewood back and sides\u003c/li\u003e\u003cli\u003eEuropean maple neck in a soft C-shaped profile\u003c/li\u003e\u003cli\u003eOvangkol fingerboard and bridge\u003c/li\u003e\u003cli\u003eFishman Flex Plus-T electronics\u003c/li\u003e\u003c/ul\u003e'
# example_list = [example_string]
#
# print(extract_strings(example_list))
