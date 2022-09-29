import sqlite3
import re
import json
from sqlite3 import Error
from db.account import Account
from db.movie import Movie
from db.review import Review
from operator import itemgetter
from werkzeug.security import generate_password_hash, check_password_hash



# Initial values for popularity of movies
# popularity = sum(ratings) + INITIAL_RATING*INITIAL_WEIGHT / num(ratings) + INITIAL WEIGHT
INITIAL_RATING = 3.5
INITIAL_WEIGHT = 3

# regex function
def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None

# create connection to db file
def create_connection(db):
    conn = None
    try:
        conn = sqlite3.connect(db)
    except Error as e:
        print(e)

    # add regex function to db
    conn.create_function('REGEXP', 2, regexp)
    return conn


# search title
def search_title(conn, keyword):
    cur = conn.cursor()
    print(keyword)
    query = (f"SELECT id FROM movies WHERE title REGEXP \"(?i).*{keyword}.*\"")

    print(query)
    cur.execute(query)

    matchs = []
    rows = cur.fetchall()
    cur.close()
    
    for i in rows:
        matchs.append(i[0])

    return matchs


# search director
def search_director(conn, keyword):
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM movies WHERE director REGEXP '(?i).*{keyword}.*'")

    matchs = []
    rows = cur.fetchall()
    cur.close()
    
    for i in rows:
        matchs.append(i[0])

    return matchs

# search genre
def search_genre(conn, keyword):
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM movies WHERE genres REGEXP '(?i).*{keyword}.*'")

    matchs = []
    rows = cur.fetchall()
    cur.close()

    for i in rows:
        matchs.append(i[0])

    return matchs

# Get similar movies to given movie_id
def get_similar(conn, movie_id, genres = [], by_director = True, banlist=[]):
    cur = conn.cursor()
    movie = get_movie(conn, movie_id)
    similar = set()
    l = []
    # get movies by the same director
    if by_director:
        cur.execute(f"SELECT id FROM movies WHERE director='{movie.director}'")

        movies = cur.fetchall()
        for i in movies:
            similar.add(i[0])
        
    for genre in genres:
        movies = search_genre(conn, genre)
        for i in movies:
            similar.add(i)
    if movie_id in similar: similar.remove(movie_id)
    for i in similar:
        l.append((i, get_rating(conn, i, banlist)))
    l.sort(key=itemgetter(1), reverse=True)

    return(l)

# get movie title given movie id
def get_title(conn, movie_id):
    cur = conn.cursor()
    cur.execute(f"SELECT title FROM movies WHERE id={movie_id}")
    name = cur.fetchall()[0][0]
    cur.close()
    return name

# get movie details given movie id
def get_movie(conn, movie_id):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM movies WHERE id={movie_id}")


    uid, title, date, director, genres, image, n_reviews, overview, tagline, runtime = cur.fetchall()[0]


    genres = json.loads(genres)

    cur.close()
    movie = Movie(uid, title, date, director, genres, image, n_reviews, overview, tagline, runtime)
    return movie



# create a review 
# return 0 on success/ 1 on error
def create_review(conn, author_id, movie_id, rating, content):
    cur = conn.cursor()

    try:
        cur.execute(f"INSERT INTO reviews (author_id, movie_id, rating, content) VALUES (?,?,?,?)", (author_id, movie_id, rating, content))

        conn.commit()
        cur.close()
        return 0
    except Error as e:
        print(e)
        cur.close()
        return 1

# create a review 
# return 0 on success/1 on error
def delete_review(conn, review_id):
    cur = conn.cursor()

    try:
        cur.execute(f"DELETE FROM reviews WHERE id={review_id}")
        conn.commit()
        return 0
    except Error as e:
        print(e)
        return 1

def update_review_rating(conn, review_id, new_rating):
    cur = conn.cursor()
    cur.execute(f"UPDATE reviews SET rating={new_rating} WHERE id={review_id}")
    conn.commit()
    cur.close()

def update_review_content(conn, review_id, new_content):
    cur = conn.cursor()
    cur.execute(f"UPDATE reviews SET content=? WHERE id=?", (new_content, review_id))
    conn.commit()
    cur.close()

# get review details given review_id
def get_review(conn, review_id):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM reviews WHERE id={review_id}")

    data = cur.fetchall()[0]

    review_id, author_id, movie_id, rating, content = data[0], data[1], data[2], data[3], data[4]

    cur.execute(f"SELECT username FROM accounts WHERE id={author_id}")

    author_name = cur.fetchall()[0][0]

    cur.close()
    review = Review(review_id, author_id, author_name, movie_id, rating, content)
    return review


# get reviews by account
def get_reviews_by_user(conn, uid):
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM reviews WHERE author_id={uid}")

    data = cur.fetchall()
    reviews = []
    for i in data:
        reviews.append(i[0])

    cur.close()
    return reviews

# get reviews by movie
def get_reviews_by_movie(conn, movie_id, banlist = []):
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM reviews WHERE movie_id={movie_id} AND author_id NOT IN ({','.join(map(str, banlist))})")

    data = cur.fetchall()
    reviews = []
    for i in data:
        reviews.append(i[0])

    cur.close()
    return reviews


# returns the number of reviews for a particular movie
def num_movie_reviews(conn, movie_id):
    cur = conn.cursor()
    cur.execute(f"SELECT count(id) FROM reviews WHERE movie_id={movie_id}")

    num = cur.fetchall()[0]

    cur.close()
    return num

def create_account(conn, username, password, email):

    # Adding the account to the database
    cur = conn.cursor()
    password = generate_password_hash(password, method='sha256')
    cur.execute(f"INSERT INTO accounts(username, password, email, wishlist, banlist) VALUES (?, ?, ?, '[]', '[]')", (username, password, email))
    conn.commit()

    # Returning the account
    account =  get_email_account(conn, email)
   
    cur.close()
    return(account)


# gets the wishlist of an user account given the user id
def get_wishlist(conn, uid):
    cur = conn.cursor()

    cur.execute(f"SELECT wishlist FROM accounts WHERE id={uid}")

    wishlist = json.loads(cur.fetchall()[0][0])
    cur.close()
    return(wishlist)


# get the banlist of a user
def get_banlist(conn, uid):
    cur = conn.cursor()
    cur.execute(f"SELECT banlist FROM accounts WHERE id={uid}")

    banlist = json.loads(cur.fetchall()[0][0])
    cur.close()
    return(banlist)

# adds a user from the user's banlist
def add_user_to_banlist(conn, uid, banned_id):

    banlist = get_banlist(conn, uid)
    banlist.append(banned_id)

    cur = conn.cursor()

    banlist = json.dumps(banlist)
    cur.execute(f"UPDATE accounts SET banlist = '{banlist}' WHERE id = {uid}")
    conn.commit()
    cur.close()

# removes a user from the user's banlist
def remove_user_from_banlist(conn, uid, banned_id):

    banlist = get_banlist(conn, uid)
    banlist.remove(banned_id)

    cur = conn.cursor()

    banlist = json.dumps(banlist)
    cur.execute(f"UPDATE accounts SET banlist = '{banlist}' WHERE id = {uid}")
    conn.commit()
    cur.close()

# adds a movie to a users wishlist
def add_movie_to_wishlist(conn, uid, movie_id):

    wishlist = get_wishlist(conn, uid)
    wishlist.append(movie_id)

    cur = conn.cursor()

    wishlist = json.dumps(wishlist)
    cur.execute(f"UPDATE accounts SET wishlist = '{wishlist}' WHERE id = {uid}")
    conn.commit()
    cur.close()

# adds a movie to a users wishlist
def remove_movie_from_wishlist(conn, uid, movie_id):

    wishlist = get_wishlist(conn, uid)
    wishlist.remove(movie_id)

    cur = conn.cursor()

    wishlist = json.dumps(wishlist)
    cur.execute(f"UPDATE accounts SET wishlist = '{wishlist}' WHERE id = {uid}")
    conn.commit()
    cur.close()



def get_account(conn, uid):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM accounts WHERE id={uid}")

    uid, password, username, email, wishlist, banlist = cur.fetchall()[0]
    wishlist = json.loads(wishlist)
    banlist = json.loads(banlist)
    account = Account(uid, password, username, email, wishlist, banlist)
    
    cur.close()
    return(account)


def get_email_account(conn, email):
    cur = conn.cursor()
    cur.execute("SELECT * FROM accounts WHERE email = ?", (email,))

    uid, password, username, email, wishlist, banlist = cur.fetchall()[0]
    wishlist = json.loads(wishlist)
    banlist = json.loads(banlist)
    account = Account(uid, password, username, email, wishlist, banlist)
    cur.close()
    return(account)

def get_rating(conn, movie_id, banlist = []):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM reviews WHERE movie_id={movie_id}")
    data = cur.fetchall()
    total = INITIAL_WEIGHT*INITIAL_RATING;
    n = INITIAL_WEIGHT;
    # if author_id is in banlist don't count the review
    for i in data:
        if i[1] not in banlist:
            total += i[3]
            n += 1
    # handle divide by zero

    try:
        if n == INITIAL_WEIGHT:
            return 0
        else:
            return total/n
    except ZeroDivisionError:
        return 0


def has_user_reviewed(conn, movie_id, author_id):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM reviews WHERE movie_id={movie_id} AND author_id = {author_id}")
    data = cur.fetchone()
    cur.close()
    if data == None:
        return False
    return True


# get the n highest rated movies 
def get_highest_rated(conn, n, banlist = []):
    cur = conn.cursor()
    cur.execute(f"SELECT movie_id FROM reviews WHERE author_id NOT IN ({','.join(map(str, banlist))}) GROUP BY movie_id ORDER BY avg(rating) DESC LIMIT {n}")
    data = cur.fetchall()
    movies = []
    for i in data:
        movies.append(i[0])
    return(movies)

# get the n most_reviewd movies
def get_most_reviewed(conn, n, banlist = []):
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM movies ORDER BY n_reviews DESC LIMIT {n}")
    data = cur.fetchall()
    movies = []
    for i in data:
        movies.append(i[0])
    return(movies)

# update an accounts username given the accounts id
def update_username(conn, user_id, new_name):
    cur = conn.cursor()
    cur.execute("UPDATE accounts SET username = ? WHERE id = ?", (new_name, user_id))
    conn.commit()
    cur.close()

# update an accounts password given the accounts id
def update_password(conn, user_id, new_pass):
    cur = conn.cursor()
    cur.execute(f"UPDATE accounts SET password = '{new_pass}' WHERE id = {user_id}")
    conn.commit()
    cur.close()

# checks if an account with given email is already registered
def is_existing_account(conn, email):
    email = str(email)
    cur = conn.cursor()
    cur.execute("SELECT * FROM accounts WHERE email = ? ", (email,))
    data = cur.fetchone()
    cur.close()
    if data == None:
        return False
    return True

def main():
    conn = create_connection("movies.db")
    with conn:
        acc = get_account(conn, '1')
        print(acc.wishlist)

if __name__ == '__main__':
    main()


