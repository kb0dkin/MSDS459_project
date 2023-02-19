# Make a Review class that has attributes "name", "location", "title", "text", "rating", "pros", "cons" and "best_for"
class Review:
    def __init__(self, rating:float, title:str, text:str, author:str, date:time.datetime, pros, cons, best_for):
        self.rating = rating
        self.title = title
        self.text = text
        self.author = author
        self.date = date
        self.pros = pros
        self.cons = cons
        self.best_for = best_for

    def __str__(self):
        return f"{self.title} by {self.author}:{self.rating}/5\n {self.text}"

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
        return f"{self.model}, {self.rating}, {self.num_ratings}, {self.price}, {self.description}, {self.item_num}, {self.pos_num}, {self.features}, {self.specs}, {self.reviews}, {self.url}"