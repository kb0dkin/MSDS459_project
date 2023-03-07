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

    # this is ugly, I'm sure there's a better way to do it 
    def insert(self, guitar_id:edgedb.pgproto.pgproto.UUID, client:edgedb.Client):

        # initialize the setup
        # query_str = 'INSERT review { '
       
        rating = self.rating if  not None else []
        rev_date = self.date if  not None else []
        pros = self.pros if len(self.pros) > 0 else []
        cons = self.cons if len(self.cons) > 0 else []
        best_for = self.best_for if len(self.best_for) > 0 else []
        text = self.text if not None else []

        query_str = """INSERT Review {
                        normalized_rating := <float64>$rating,
                        date := <std::datetime>$rev_date, 
                        pros := <array<str>>$pros,
                        cons := <array<str>>$cons,
                        best_for := <array<str>>$best_for,
                        written_review := <str>$text,
                        guitar := (
                            SELECT Guitar
                            filter .id = <uuid>$guitar_id
                            )
                        }
                        """
        client.query(query_str, rating=rating, rev_date=rev_date, pros=pros,\
                     cons = cons, best_for = best_for, text = text, guitar_id = guitar_id)

        # if self.rating is not None:
            # query_str = query_str + f"normalized_rating: <float64><decimal>{self.rating}, "
        # if self.date is not None:
            # query_str = query_str + f"date := <std::datetime>>'{self.date}', "
        # if self.pros is not None:
        #     query_str = query_str + f"pros := <array<str>>{self.pros}, "
        # if self.cons is not None:
        #     query_str = query_str + f"cons := <array<str>>{self.cons}, "
        # if self.best_for is not None:
        #     query_str = query_str + f"best_for := <array<str>>{self.best_for}, "
        # if self.text is not None:
        #     query_str = query_str + f"written_review := <str>'{self.text}', "
        
        # # link the guitar
        # query_str = query_str + f"""
        #                         guitar := (
        #                             SELECT Guitar
        #                             filter
        #                                 .id = <uuid>{guitar_id}
        #                         )
        #                         """
        
        # # close it out
        # query_str = query_str + '}'

        # return client.query(query_str)
        return query_str





# Make a Guitar class 
#       Contains a constructor, a function to allow it to print
#       and (most importantly) a parser to insert into the database
class Guitar:
    def __init__(self, model:str, description:str = None, features = None, specs = None,\
                body_shape:str = None, cutaway:str = None, pickups:str = None,\
                num_strings:int = None, scale_length:float = None, num_frets:int = None,\
                country_of_origin:str = None, manufacturer:str = None, guitar_type:str = 'Unknown'):
        
        # fill everything out
        self.model = model #
        self.description = description
        self.features = features
        self.body_shape = body_shape
        self.cutaway = cutaway
        self.pickups = pickups #
        self.num_strings = num_strings
        self.scale_length = scale_length
        self.num_frets = num_frets
        self.country_of_origin = country_of_origin
        self.specs = specs #
        self.guitar_type = guitar_type
        self.manufacturer = manufacturer


    # instantiating string methods
    def __str__(self):
        return f"{self.model}, {self.description}, {self.features}, {self.specs}"
    
    def keys(self):
        return self.__dict__.keys()
    

    
    # insert into the database
    #   this has to account for null fields by not adding them
    def insert(self, client:edgedb.Client):
        query_str = "INSERT Guitar {"
        
        # there's got to be a better way .gif.... maybe a dictionary?
        # start with the mandatory stuff
        query_str = query_str + f"model := <str>'{self.model}', " # model name
        query_str = query_str + f"type := <str>'{self.guitar_type}', " # guitar type
        # non-mandatory stuff
        if self.description is not None:
            query_str = query_str + f"description := <str>'{self.description}', "
        if self.body_shape is not None:
            query_str = query_str + f"body_shape: <str>'{self.body_shape}', "
        if self.cutaway is not None:
            query_str = query_str + f"cutaway: <str>'{self.cutaway}', "
        if self.num_strings is not None:
            query_str = query_str + f"num_strings := <int32>{self.num_strings}, "
        if self.scale_length is not None:
            query_str = query_str + f"scale_length := <float64>{self.scale_length}, "
        if self.num_frets is not None:
            query_str = query_str + f"num_frets := <int32>{self.num_frets}, "

        # now for a complicated one -- the manufacturer!
        if self.manufacturer is not None:
            query_str = query_str + f""" brand := ( 
                                        INSERT Manufacturer {{
                                            name := <str>'{self.manufacturer}'
                                        }}
                                        UNLESS CONFLICT ON Manufacturer.name
                                        ELSE Manufacturer
                                        )
                                    """

        query_str = query_str + "}"

        # return query_str
        return client.query(query_str)[0].id # return the guitar id


class Manufacturer:
    def __init__(self, name):
        self.name = name

