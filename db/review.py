import db.db


class Review():

    def __init__(self, review_id, author_id, author_name, movie_id, rating, content):
        self._id = review_id
        self._author_id = author_id
        self._author_name = author_name
        self._movie_id = movie_id
        self._rating = rating
        self._content = content

    @property
    def id(self):
        return self._id
    
    @property
    def author_id(self):
        return self._author_id

    @property
    def author_name(self):
        return self._author_name

    @property
    def movie_id(self):
        return self._movie_id
    
    @property
    def rating(self):
        return(self._rating)

    @property
    def content(self):
        return(self._content)

    def change_rating(self, conn, new_rating):
        db.update_review_rating(conn, self._id, new_rating)
        self._rating = new_rating
        return new_rating

    def change_content(self, conn, new_content):
        db.update_review_content(conn, self._id, new_content)
        self._content = new_content
        return new_content
