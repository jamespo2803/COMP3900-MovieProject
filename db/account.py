import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
#from . import db 
#from db import add_movie_to_wishlist, remove_movie_from_wishlist, create_connection


class Account(UserMixin):

    def __init__(self, id, password, username, email, wishlist, banlist):
        self._id = id
        self._password = password
        self._username = username
        self._email = email
        self._wishlist = wishlist
        self._banlist = banlist


    # add a movie to the wishlist
    def add_movie(self, conn, movie_id):
        self._wishlist.append(movie_id)
        db.add_movie_to_wishlist(conn, self.id, movie_id)

    # remove a movie from the wishlist
    def remove_movie(self, conn, movie_id):
        self._wishlist.remove(movie_id)
        db.remove_movie_from_wishlist(conn, self.id, movie_id)

    def get_reviews(self, conn):
        reviews = db.get_reviews_by_user(conn, self.id)
        return reviews

    def change_username(self, conn, new_username):
        self._username = new_username
        db.update_username(conn, self._id, new_username)

    def change_pass(self, conn, new_pass):
        new_pass = generate_password_hash(new_pass, method='sha256')
        self._password = new_pass
        db.update_password(conn, self._id, new_pass)


    @property
    def id(self):
        return self._id
    
    @property
    def username(self):
        return self._username
    
    @property
    def password(self):
        return self._password
    

    @property
    def email(self):
        return self._email
    
    @property
    def wishlist(self):
        return self._wishlist

    # banlist getter
    @property
    def banlist(self):
        return(self._banlist)

    @property
    def is_authenticated(self):
        return True

    # add a user to the banlist
    def add_to_ban_list(self, conn, banned_id):
        if banned_id != self.id and banned_id not in self.banlist:
            self._banlist.append(banned_id)
            db.add_user_to_banlist(conn, self.id, banned_id)
            return 0
        else:
            return 1

    # remove a user to the banlist
    def remove_from_ban_list(self, conn, banned_id):
        if banned_id in self.banlist:
            self._banlist.remove(banned_id)
            db.remove_user_from_banlist(conn, self.id, banned_id)
            return 0
        else:
            return 1


    def set_password(self, password):
        #Create hashed password
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        #Check hashed password
        return check_password_hash(self.password, password)
