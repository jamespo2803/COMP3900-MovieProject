from flask import Flask, render_template, Blueprint, request, redirect, url_for, flash
from controller.controller import *
from db.db import *
from flask_login import login_required, current_user

SEARCH_RESULTS_PER_PAGE = 20
REVIEWS_PER_PAGE = 10
USER_REVIEWS_PER_PAGE = 5
WISHES_PER_PAGE = 6

routes_bp = Blueprint('routes_bp',__name__)

@routes_bp.route('/', methods=["GET", "POST"])
def home():
    # Get most popular movies.
    conn = create_connection("db/movies.db")
    banlist = []
    if (current_user.is_authenticated):
        banlist = current_user.banlist
    popular_movies = get_highest_rated(conn, 7, banlist)

    movies = []
    for i in popular_movies:
        movie = get_movie(conn, i)
        movies.append(movie)
    # Done, return rendered page.
    return render_template('pages/home.html', movies=movies, banlist = banlist, conn=conn)

@routes_bp.route('/search', methods=["GET", "POST"])
def search():
    if(request.method == 'POST'):
        form = request.form
        if 'search_options' and 'search' in form:
            return redirect(url_for('routes_bp.search_result', search_term=form['search'], search_type=form['search_options']))
    return render_template('pages/home.html')

@routes_bp.route('/search/<search_type>/<search_term>', methods=["GET", "POST"])
def search_result(search_term, search_type):
    conn = create_connection("db/movies.db")
    mov_list = []
    search_no = 0
    if search_type == 'Director':
        results = searchQuickDirector(conn, search_term)
        result_no = len(results)        
    elif search_type == 'Genre':
        results = searchQuickGenre(conn, search_term)
        result_no = len(results)
    else:
        results = searchQuick(conn, search_term)
        result_no = len(results)
    for result in results:
        mov_list.append(get_movie(conn, result[0]))  
        if len(mov_list) >= SEARCH_RESULTS_PER_PAGE:
            break
    total_pages=result_no//SEARCH_RESULTS_PER_PAGE+(result_no%SEARCH_RESULTS_PER_PAGE > 0)

    if current_user.is_authenticated:
        banlist = current_user.banlist
    else:
        banlist = []

    return render_template('pages/search.html', search_term=search_term, mov_list=mov_list, search_type=search_type, 
        page_no=1, total_pages=total_pages, result_no=result_no, banlist=banlist, conn=conn)

@routes_bp.route('/search/<search_type>/<search_term>/page/<int:page_no>', methods=["GET", "POST"])
def search_result_pages(search_term, search_type, page_no):
    conn = create_connection("db/movies.db")
    mov_list = []
    if search_type == 'Director':
        results = searchQuickDirector(conn, search_term)
        result_no = len(results)
    elif search_type == 'Genre':
        results = searchQuickGenre(conn, search_term)
        result_no = len(results)
    else:
        results = searchQuick(conn, search_term)
        result_no = len(results)
    for count, result in enumerate(results):
        if count < (page_no-1)*SEARCH_RESULTS_PER_PAGE:
            continue
        mov_list.append(get_movie(conn, result[0]))  
        if len(mov_list) >= SEARCH_RESULTS_PER_PAGE:
            break
    total_pages=result_no//SEARCH_RESULTS_PER_PAGE+(result_no%SEARCH_RESULTS_PER_PAGE > 0)

    if current_user.is_authenticated:
        banlist = current_user.banlist
    else:
        banlist = []

    return render_template('pages/search.html', search_term=search_term, mov_list=mov_list, search_type=search_type, 
        page_no=page_no, total_pages=total_pages, result_no=result_no, banlist=banlist, conn=conn)

@routes_bp.route('/profile/id/<int:user_id>/wishlist', methods=["GET", "POST"])
def wishlist(user_id):
    form = request.form
    conn = create_connection("db/movies.db")

    account = get_account(conn, user_id)
    wishList = getWishlist(conn, user_id)
    wish_no = len(wishList)
    wishes = []
    i = 0
    for count in enumerate(wishList):
        if len(wishes) < WISHES_PER_PAGE:
            wishes.append(wishList[i]) 
        i += 1
    total_pages=wish_no//WISHES_PER_PAGE+(wish_no%WISHES_PER_PAGE > 0)
    
    if(request.method == 'POST'):
        form = request.form
        if 'remove' in form:
            movID = int(request.form['remove'])
            account.remove_movie(conn, movID)
            wishList = getWishlist(conn, user_id)
            conn.close()
            return redirect(request.referrer)
        conn.close()
        return render_template('pages/wishlist.html', username = account.username, wishlist = wishes, curruser = current_user.id, userid = user_id, page_no = 1, total_pages = total_pages)
    conn.close()
    if (not current_user.is_authenticated):
        return render_template('pages/wishlist.html', username = account.username, wishlist = wishes, curruser = -1, userid = user_id, page_no = 1, total_pages = total_pages)
    return render_template('pages/wishlist.html', username = account.username, wishlist = wishes, curruser = current_user.id, userid = user_id, page_no = 1, total_pages = total_pages)
    
@routes_bp.route('/profile/id/<int:user_id>/wishlist/<int:page_no>', methods=["GET", "POST"])
def wishlist_pages(user_id, page_no):
    form = request.form
    conn = create_connection("db/movies.db")

    account = get_account(conn, user_id)
    wishList = getWishlist(conn, user_id)
    wish_no = len(wishList)
    wishes = []
    i = 0
    for count in enumerate(wishList):
        if i >= (page_no-1)*WISHES_PER_PAGE and len(wishes) < WISHES_PER_PAGE:
            wishes.append(wishList[i]) 
        i += 1
    total_pages=wish_no//WISHES_PER_PAGE+(wish_no%WISHES_PER_PAGE > 0)
    
    if(request.method == 'POST'):
        form = request.form
        if 'remove' in form:
            movID = int(request.form['remove'])
            account.remove_movie(conn, movID)
            wishList = getWishlist(conn, user_id)
            conn.close()
            return redirect(request.referrer)
        conn.close()
        return render_template('pages/wishlist.html', username = account.username, wishlist = wishes, curruser = current_user.id, userid = user_id, page_no = page_no, total_pages = total_pages)
    conn.close()
    if (not current_user.is_authenticated):
        return render_template('pages/wishlist.html', username = account.username, wishlist = wishes, curruser = -1, userid = user_id, page_no = page_no, total_pages = total_pages)
    return render_template('pages/wishlist.html', username = account.username, wishlist = wishes, curruser = current_user.id, userid = user_id, page_no = page_no, total_pages = total_pages)

@routes_bp.route('/profile/id/<int:user_id>/banlist', methods=["GET", "POST"])
def banlist(user_id):
    form = request.form
    conn = create_connection("db/movies.db")
    account = get_account(conn, user_id)
    banList = getBanList(conn, user_id)
    if(request.method == 'POST'):
        form = request.form
        if 'remove' in form:
            unbanID = int(request.form['remove'])
            account.remove_from_ban_list(conn, unbanID)
            banList = getBanList(conn, user_id)
            return redirect(request.referrer)
        return redirect(request.referrer)
    if (not current_user.is_authenticated):
        return render_template('pages/banlist.html', username = account.username, banlist = banList, curruser = -1, userid = user_id)
    conn.close()
    return render_template('pages/banlist.html', username = account.username, banlist = banList, curruser = current_user.id, userid = user_id)

@routes_bp.route('/profile/id/<int:user_id>/reviews', methods=["GET", "POST"])
def user_reviews(user_id):
    form = request.form
    conn = create_connection("db/movies.db")
    account = get_account(conn, user_id)
    reviews = getUserReviews(conn, user_id)
    review_no = len(reviews)
    reviewList = []
    i = 0
    for count in enumerate(reviews):
        if len(reviewList) < USER_REVIEWS_PER_PAGE:
            reviewList.append(reviews[i]) 
        i += 1
    total_pages=review_no//USER_REVIEWS_PER_PAGE+(review_no%USER_REVIEWS_PER_PAGE > 0)
    
    movies = []
    for review in reviewList:
       movies.append(get_movie(conn, review.movie_id))
    if (not current_user.is_authenticated):
        curruser = -1
    else:
        curruser = current_user.id
    return render_template('pages/user_reviews.html', username = account.username, curruser = curruser, userid = user_id, reviews = reviewList, movies = movies, n_reviews=len(reviewList), page_no = 1, total_pages = total_pages)

@routes_bp.route('/profile/id/<int:user_id>/reviews/<int:page_no>', methods=["GET", "POST"])
def user_reviews_pages(user_id, page_no):
    form = request.form
    conn = create_connection("db/movies.db")
    account = get_account(conn, user_id)
    reviews = getUserReviews(conn, user_id)
    review_no = len(reviews)
    reviewList = []
    i = 0
    for count in enumerate(reviews):
        if i >= (page_no-1)*USER_REVIEWS_PER_PAGE and len(reviewList) < USER_REVIEWS_PER_PAGE:
            reviewList.append(reviews[i]) 
        i += 1
    total_pages=review_no//USER_REVIEWS_PER_PAGE+(review_no%USER_REVIEWS_PER_PAGE > 0)
    
    movies = []
    for review in reviewList:
       movies.append(get_movie(conn, review.movie_id))
    if (not current_user.is_authenticated):
        curruser = -1
    else:
        curruser = current_user.id
    return render_template('pages/user_reviews.html', username = account.username, curruser = curruser, userid = user_id, reviews = reviewList, movies = movies, n_reviews=len(reviewList), page_no = page_no, total_pages = total_pages)


@routes_bp.route('/profile/id/<int:user_id>', methods=["GET", "POST"])
#@login_required
def profile(user_id):
    conn = create_connection("db/movies.db")
    acc = get_account(conn, user_id)
    if(request.method == 'POST'):
        form = request.form
        if 'ban' in form:
            banID = int(request.form['ban'])
            current_user.add_to_ban_list(conn, banID)
            banned = 1
            return render_template('pages/profile.html', acc=acc, curruser = current_user.id, user_id = user_id, banned = banned)
        elif 'unban' in form:
            banID = int(request.form['unban'])
            current_user.remove_from_ban_list(conn, banID)
            banned = 0
        return redirect(request.referrer)
    if (not current_user.is_authenticated):
        return render_template('pages/profile.html', acc=acc, curruser = -1, user_id = user_id, banned = 0)
    banned = checkBanlist(conn, current_user.id, user_id)
    return render_template('pages/profile.html', acc=acc, curruser = current_user.id, user_id = user_id, banned = banned)

@routes_bp.route('/profile/id/<int:user_id>/change_details', methods=["GET", "POST"])
@login_required
def change_profile_details(user_id):
    if current_user.id != user_id:
        return render_template('pages/home.html')
    conn = create_connection("db/movies.db")
    if(request.method == 'POST'):
        form = request.form
        if 'change_username' in form:
            if len(form['change_username']) < 1:   
                return render_template('pages/change_profile_details.html', username_error="Username must be longer")
            current_user.change_username(conn,form['change_username'])
            return render_template('pages/change_profile_details.html', username_confirm="Username changed")
        elif 'change_new_pass' in form:
            if current_user.check_password(form['change_old_pass']):
                if len(form['change_new_pass']) < 6:
                    return render_template('pages/change_profile_details.html', new_pass_error="Password must be 6 characters or longer")
                current_user.change_pass(conn,form['change_new_pass'])
                return render_template('pages/change_profile_details.html', pass_confirm="Password changed")
            else:
                return render_template('pages/change_profile_details.html', old_pass_error="Password does not match")
    conn.close()
    return render_template('pages/change_profile_details.html')

@routes_bp.route('/movies/<int:movie_id>', methods=["GET", "POST"])
def movie(movie_id):
    conn = create_connection("db/movies.db")
    form = request.form
    rating_error = None
    review_error = None
    movie = get_movie(conn, movie_id)
    
    edit = 0
    err = 0
    # handle if user is logged in
    user_review = None
    has_reviewed = False
    if current_user.is_authenticated:
        banlist = current_user.banlist
        subscribed = checkWishlist(conn,current_user.id, movie_id)
        if has_user_reviewed(conn, movie.id, current_user.id):
            has_reviewed = True
    else:
        banlist = []
        subscribed = 0


    # get reviews
    review_list = get_reviews_by_movie(conn, movie_id, banlist)
    review_no = len(review_list)
    reviews = []

    for count, result in enumerate(review_list):
        if has_reviewed == True and get_review(conn, result).author_id == current_user.id:
            user_review = get_review(conn, result)
        elif len(reviews) < REVIEWS_PER_PAGE:
            reviews.append(get_review(conn, result))
    total_pages=review_no//REVIEWS_PER_PAGE+(review_no%REVIEWS_PER_PAGE > 0)

    rating = movie.get_rating(conn, banlist)

    similar_movies_genre_list = movie.genres
    similar_movies_director = True

    if(request.method == 'POST'):
        form = request.form
        if 'add' in form:
            movID = int(request.form['add'])
            current_user.add_movie(conn, movID)
            subscribed = 1
            return redirect(request.referrer)
        elif 'remove' in form:
            movID = int(request.form['remove'])
            current_user.remove_movie(conn, movID)
            subscribed = 0
            return redirect(request.referrer)
        elif 'edit_review' in form:
            edit = 1
        elif 'update' in form:
            revID = int(request.form['update'])
            err = 0
            if 'rating' not in form and 'new_review' in form:
                err = 1
                rating_error = "must choose a rating"
            if 'new_review' in form and form['new_review'] == "":
                err = 1
                review_error = "must type a review"
            if err == 0:
                editReview(conn, revID, form['rating'], form['new_review'])
                edit = 0
            else:
                edit = 1
            return redirect(request.referrer)
        elif 'cancel' in form:
            edit = 0
            return redirect(request.referrer)
        elif 'new_review' and 'rating' in form and form['new_review'] != "":
            create_review(conn, current_user.id, movie.id, form['rating'], form['new_review'])
            return redirect(request.referrer)
        elif 'remove_review' in form:
            revID = int(request.form['remove_review'])
            removeReview(conn, revID)
            return redirect(request.referrer)
        

        if 'similar_movies_updated' in form:
            if 'similar_movies_director' in form:
                similar_movies_director = True
            else:
                similar_movies_director = False
            if 'similar_movies_genre_list' in form:
                similar_movies_genre_list = request.form.getlist('similar_movies_genre_list')
            else:
                similar_movies_genre_list = []

            

        if 'rating' not in form and 'new_review' in form:
            rating_error = "must choose a rating"
        if 'new_review' in form and form['new_review'] == "":
            review_error = "must type a review"


    s = get_similar(conn, movie_id, genres = similar_movies_genre_list, by_director = similar_movies_director, banlist=banlist)
    similar_movies = []
    for i in s:
        similar_movies.append(get_movie(conn, i[0]))

    return render_template('pages/movie.html', movie=movie, movie_id=movie_id, subscribed=subscribed, reviews=reviews, 
        review_no=review_no, rating=rating, rating_error=rating_error, review_error=review_error, has_reviewed=has_reviewed, 
        user_review=user_review, similar_movies=similar_movies, conn=conn, similar_movies_genre_list=similar_movies_genre_list,
        similar_movies_director=similar_movies_director, edit = edit, err= err, review_page_no=1, total_pages=total_pages)

@routes_bp.route('/movies/<int:movie_id>/page/<int:review_page_no>', methods=["GET", "POST"])
def movie_review_pages(movie_id,review_page_no):
    conn = create_connection("db/movies.db")
    form = request.form
    rating_error = None
    review_error = None
    movie = get_movie(conn, movie_id)
    
    edit = 0
    err = 0
    # handle if user is logged in
    user_review = None
    has_reviewed = False
    if current_user.is_authenticated:
        banlist = current_user.banlist
        subscribed = checkWishlist(conn,current_user.id, movie_id)
        if has_user_reviewed(conn, movie.id, current_user.id):
            has_reviewed = True
    else:
        banlist = []
        subscribed = 0


    # get reviews
    review_list = get_reviews_by_movie(conn, movie_id, banlist)
    review_no = len(review_list)
    reviews = []

    for count, result in enumerate(review_list):
        if has_reviewed == True and get_review(conn, result).author_id == current_user.id:
            user_review = get_review(conn, result)
        elif count >= (review_page_no-1)*REVIEWS_PER_PAGE and len(reviews) < REVIEWS_PER_PAGE:
            reviews.append(get_review(conn, result)) 
    total_pages=review_no//REVIEWS_PER_PAGE+(review_no%REVIEWS_PER_PAGE > 0)
    
    rating = movie.get_rating(conn, banlist)

    similar_movies_genre_list = movie.genres
    similar_movies_director = True

    if(request.method == 'POST'):
        form = request.form
        if 'add' in form:
            movID = int(request.form['add'])
            current_user.add_movie(conn, movID)
            subscribed = 1
            conn.close()
            return redirect(request.referrer)
        elif 'remove' in form:
            movID = int(request.form['remove'])
            current_user.remove_movie(conn, movID)
            subscribed = 0
            conn.close()
            return redirect(request.referrer)
        elif 'edit_review' in form:
            edit = 1
        elif 'update' in form:
            revID = int(request.form['update'])
            err = 0
            if 'rating' not in form and 'new_review' in form:
                err = 1
                rating_error = "must choose a rating"
            if 'new_review' in form and form['new_review'] == "":
                err = 1
                review_error = "must type a review"
            if err == 0:
                editReview(conn, revID, form['rating'], form['new_review'])
                edit = 0
            else:
                edit = 1
                conn.close()
                return render_template('pages/movie_review_pages.html', movie=movie, movie_id=movie_id, subscribed=subscribed, reviews=reviews, 
                    review_no=review_no, rating=rating, rating_error=rating_error, review_error=review_error, has_reviewed=has_reviewed, 
                    user_review=user_review, edit = edit, err= err, review_page_no=review_page_no, total_pages=total_pages)
            conn.close()
            return redirect(request.referrer)
        elif 'cancel' in form:
            edit = 0
            conn.close()
            return redirect(request.referrer)
        elif 'new_review' and 'rating' in form and form['new_review'] != "":
            create_review(conn, current_user.id, movie.id, form['rating'], form['new_review'])
            conn.close()
            return redirect(request.referrer)
        elif 'remove_review' in form:
            revID = int(request.form['remove_review'])
            removeReview(conn, revID)
            conn.close()
            return redirect(request.referrer)
        


        if 'similar_movies_updated' in form:
            if 'similar_movies_director' in form:
                similar_movies_director = True
            else:
                similar_movies_director = False
            if 'similar_movies_genre_list' in form:
                similar_movies_genre_list = request.form.getlist('similar_movies_genre_list')
            else:
                similar_movies_genre_list = []

            

        if 'rating' not in form and 'new_review' in form:
            rating_error = "must choose a rating"
        if 'new_review' in form and form['new_review'] == "":
            review_error = "must type a review"


    s = get_similar(conn, movie_id, genres = similar_movies_genre_list, by_director = similar_movies_director, banlist=banlist)
    similar_movies = []
    for i in s:
        similar_movies.append(get_movie(conn, i[0]))
    conn.close()

    return render_template('pages/movie.html', movie=movie, movie_id=movie_id, subscribed=subscribed, reviews=reviews, 
        review_no=review_no, rating=rating, rating_error=rating_error, review_error=review_error, has_reviewed=has_reviewed, 
        user_review=user_review, similar_movies=similar_movies, conn=conn, similar_movies_genre_list=similar_movies_genre_list,
        similar_movies_director=similar_movies_director, edit = edit, err= err, review_page_no=review_page_no, total_pages=total_pages)