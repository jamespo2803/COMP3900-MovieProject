from db.db import *
from db.account import *
import json
import re

def splitText(searchText):

    l = searchText.split()

    for i in range(0, len(l)):
        l[i] = re.escape(l[i])
        l[i] = l[i].replace("\"", "")
    return l

    
def addGenre(genreList, newGenre):
    genreList.append(newGenre)
    return genreList
    
def searchQuick(conn, searchText):
    searchList = splitText(searchText)
    #conn = create_connection("db/movies.db")
    movList = []
    for word in searchList:
        movieIDs = search_title(conn, word)
        if movieIDs:
            for ID in movieIDs:
                if ID not in movList:
                    movList.append(ID)
    sortedList = moviesByPopularity(conn, movList)
    return sortedList

def searchQuickGenre(conn, searchText):
    searchList = splitText(searchText)
    #conn = create_connection("db/movies.db")
    movList = []
    for word in searchList:
        byGenre = search_genre(conn, word)
        if byGenre:
            for ID in byGenre:
                if ID not in movList:
                    movList.append(ID)
    sortedList = moviesByPopularity(conn, movList)
    return sortedList

def searchQuickDirector(conn, searchText):
    searchList = splitText(searchText)
    #conn = create_connection("db/movies.db")
    movList = []
    for word in searchList:
        byDirector = search_director(conn, searchText)
        if byDirector:
            for ID in byDirector:
                if ID not in movList:
                    movList.append(ID)
    sortedList = moviesByPopularity(conn, movList)
    return sortedList


def moviesByPopularity(conn, movieIDsList):
    results = []
    for ID in movieIDsList:
        rating = get_rating(conn, ID)
        movie = (ID, rating)
        results.append(movie)
    results.sort(key=itemgetter(1), reverse=True)
    return results



def searchFullName(searchText, conn):
    return search_title(conn, searchText)
    
def searchGenre(conn, genreList):
    movList = []
    for genre in genreList:
        #call search on each genre
        #void(genre)
        #print(genre)
        movList.append(search_genre(conn, genre))
        #print(movList)
    
def checkWishlist(conn, user, movid):
    wList = getWishlist(conn,user)
    for wish in wList:
        if wish.id == movid:
            return 1
    return 0
    
def checkBanlist(conn, user, banid):
    bList = getBanList(conn,user)
    for ban in bList:
        if ban.id == banid:
            return 1
    return 0
    
def getBanList(conn, userID):
    acc = get_account(conn, userID)
    #acc.add_to_ban_list(conn, 2)
    bans = acc.banlist
    banList = []
    for ban in bans:
        banList.append(get_account(conn, str(ban)))
        #print(ban)
    return banList
    
def getWishlist(conn, user):
    acc = get_account(conn,user)
    #add_movie_to_wishlist(conn,17,1)
    #acc.remove_movie(1092)
    #remove_movie_from_wishlist(conn, 1, 1092)
    wList = acc.wishlist
    #print(len(wList))
    #print(acc.get_wishlist()[1:-1])
    movList = []
    for wish in wList:
        movList.append(get_movie(conn, wish))
    return movList

def getUserReviews(conn, user):
    acc = get_account(conn, user)
    reviews = acc.get_reviews(conn)
    revList = []
    for rev in reviews:
        revList.append(get_review(conn, rev))
    return revList
    
def getMovieList(conn, revList):
    movList = []
    for rev in revList:
        movList.append(get_movie(conn, rev.movie_id))
    return movList
    
def editReview(conn, revID, newStars, newReview):
    review = get_review(conn,revID)
    review.change_content(conn, newReview)
    review.change_rating(conn, newStars)
    return review
    
def removeReview(conn, revID):
    delete_review(conn, revID)