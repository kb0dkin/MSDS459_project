import edgedb


# Make a Review class that has attributes "name", "location", "title", "text", "rating", "pros", "cons" and "best_for"
class Review:
    def __init__(self, rating:float, title:str, text:str, author:str, date, review_source:str = 'Guitar Center'):
        self.rating = rating
        self.title = title
        self.text = text
        self.author = author
        self.date = date
        self.review_source = review_source

    def __str__(self):
        return f"{self.title} by {self.author}:{self.rating}"

    # this is ugly, I'm sure there's a better way to do it 
    def insert(self, guitar_id:edgedb.pgproto.pgproto.UUID, client:edgedb.Client):

        # initialize the setup
        # query_str = 'INSERT review { '
       
        rating = self.rating if self.rating is not None else float()
        rev_date = self.date if self.date is not None else str()
        text = self.text if self.text is not None else str()

        query_str = """INSERT Review {
                        normalized_rating := <float64>$rating,
                        date := <std::datetime>$rev_date, 
                        written_review := <str>$text,
                        guitar := (
                            SELECT Guitar
                            filter .id = <uuid>$guitar_id
                            ),
                        source :=(
                            SELECT ReviewSource
                            filter .name = <str>$review_source
                        ),
                        }
                        """
        return_val = client.query(query_str, rating=rating, rev_date=rev_date,\
                            text = text, guitar_id = guitar_id, review_source = self.review_source)

        
        # insert or update the reviewer 
        query_str = """INSERT Reviewer {
                        name := <str>$name,
                        review := (
                            SELECT Review
                            filter .id = <uuid>$review_id
                        ),
                        source := (
                            SELECT ReviewSource
                            filter .name = <str>$review_source
                        )
                    } UNLESS CONFLICT on .name
                    ELSE (
                        UPDATE Reviewer SET {
                            review += (
                                SELECT Review
                                filter .id = <uuid>$review_id
                            )
                        }
                    )
                    """
        
        reviewer_val = client.query(query_str, name=self.author, review_id = return_val[0].id, review_source = self.review_source)
        
        return return_val[0].id



# Make a Guitar class 
#       Contains a constructor, a function to allow it to print
#       and (most importantly) a parser to insert into the database
class Guitar:
    def __init__(self, model:str, description:str = None, features = None, specs = None,\
                body_shape:str = None, cutaway:str = None, pickups:str = None,\
                num_strings:int = None, scale_length:float = None, num_frets:int = None,\
                country_of_origin:str = None, manufacturer:str = None, guitar_type:str = 'Unknown',\
                pros:list = [], cons:list = [], best_for:list = [], url:str = None):

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
        self.pros = pros
        self.cons = cons
        self.best_for = best_for
        self.url = url


    # instantiating string methods
    def __str__(self):
        return f"{self.model}, {self.description}, {self.features}, {self.specs}"
    
    def keys(self):
        return self.__dict__.keys()
    
    # insert into the database
    #   this has to account for null fields by not adding them
    def insert(self, client:edgedb.Client):


        # # there's got to be a better way .gif.... maybe a dictionary?
        # replace Nones and empty lists with []
        description = self.description if self.description is not None else str()
        body_shape = self.body_shape if self.body_shape is not None else str()
        cutaway = self.cutaway if self.cutaway is not None else str()
        num_strings = self.num_strings if self.num_strings is not None else int()
        scale_length = self.scale_length if self.scale_length is not None else float()
        num_frets = self.num_frets if self.num_frets is not None else int()
        pros = self.pros if len(self.pros) > 0 else edgedb.Set()
        cons = self.cons if len(self.cons) > 0 else edgedb.Set()
        best_for = self.best_for if len(self.best_for) > 0 else edgedb.Set()
        url = self.url if self.url is not None else str()

        # create the query string
        query_str = """ INSERT Guitar {
                            model := <str>$model,
                            type := <str>$guitar_type,
                            description := <str>$description,
                            body_shape := <str>$body_shape,
                            cutaway := <str>$cutaway,
                            num_strings := <int32>$num_strings,
                            scale_length := <float64>$scale_length,
                            num_frets := <int32>$num_frets,
                            pros := <array<str>>$pros,
                            cons := <array<str>>$cons,
                            best_for := <array<str>>$best_for,
                            url := <str>$url,

                            brand := (
                                INSERT Manufacturer {
                                    name := <str>$manufacturer,
                                }
                                UNLESS CONFLICT ON Manufacturer.name
                                ELSE Manufacturer
                            ),
                            seller := (
                                SELECT Vendor filter .name = 'Guitar Center'
                            ),
                        } 
                        UNLESS CONFLICT ON .model
                    """
        resp = client.query(query_str, model=self.model, guitar_type = self.guitar_type, description=description,\
            body_shape=body_shape, cutaway=cutaway, num_strings=num_strings,\
            scale_length=scale_length, num_frets=num_frets, manufacturer=self.manufacturer,\
            pros = pros, cons = cons, best_for=best_for, url=url)

        return resp[0].id  # id of the inserted guitar



class Manufacturer:
    def __init__(self, name):
        self.name = name

