import db.db


class Movie():

    def __init__(self, uid, title, date, director, genres, image, n_reviews, overview, runtime, tagline):
        self._id = uid
        self._title = title
        self._date = date
        self._director = director
        self._genres = genres
        self._image = image
        self._n_reviews = n_reviews
        self._overview = overview
        self._runtime = runtime
        self._tagline = tagline

    # title getter
    @property
    def id(self):
        return self._id
    
    @property
    def title(self):
        return self._title

    # date getter
    @property
    def date(self):
        return(self._date)

    # director getter
    @property
    def director(self):
        return(self._director)

    @property
    def genres(self):
        return(self._genres)

    @property
    def image(self):
        return self._image
    
    @property
    def n_reviews(self):
        return self._n_reviews
    
    @property
    def overview(self):
        return self._overview
    
    @property
    def runtime(self):
        return self._runtime
    
    @property
    def tagline(self):
        return self._tagline
    

    def get_reviews(self, conn):
        reviews = db.get_reviews_by_movie(conn, self._id, banlist = [])
        return reviews


    # use n_reviews instead
    def get_num_reviews(self, conn):
        num = num_movie_reviews(conn, movie_id)
        return num

    
    def get_rating(self, conn, banlist = []):
        return round(db.get_rating(conn, self._id, banlist),2)



