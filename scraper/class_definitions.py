import edgedb


# Make a Review class that has attributes "name", "location", "title", "text", "rating", "pros", "cons" and "best_for"
class Review:
    def __init__(self, rating:float, title:str, text:str, author:str, date, pros:list, cons:list, best_for:list):
        self.rating = rating
        self.title = title
        self.text = text
        self.author = author
        self.date = date
        self.pros = pros
        self.cons = cons
        self.best_for = best_for

    def __str__(self):
        return f"{self.title} by {self.author}:{self.rating}\n {self.text}"

# Make a Guitar class that has attributes "model", "rating", "num_ratings", "price", 
# "description", "item_num", "pos_num",
# "features", "specs", "warranty", "reviews" and "url"
class Guitar:
    def __init__(self, model:str = None, description = None, features = None, specs = None,\
                body_shape:str = None, cutaway:str = None, pickups:str = None,\
                num_strings:int = None, scale_length:float = None, num_frets:int = None,\
                country_of_origin:str = None):
        
        # fill everything out
        self.model = model #
        self.description = description #
        self.features = features #
        self.body_shape = body_shape
        self.cutaway = cutaway
        self.pickups = pickups
        self.num_strings = num_strings
        self.scale_length = scale_length
        self.num_frets = num_frets
        self.country_of_origin = country_of_origin
        self.specs = specs #

    def __str__(self):
        return f"{self.model}, {self.description}, {self.features}, {self.specs}"
    

class Manufacturer:
    def __init__(self, name):
        self.name = name

