CREATE TABLE IF NOT EXISTS "movies"(
	id INTEGER primary key,
	title TEXT,
	date TEXT,
	director TEXT,
	genres TEXT, 
	image TEXT, 
	n_reviews INTEGER, 
	overview TEXT, 
	tagline TEXT,
	runtime TEXT
);

CREATE TABLE IF NOT EXISTS "reviews"(
	id INTEGER primary key,
	author_id INTEGER,
	movie_id INTEGER,
	rating INTEGER,
	content TEXT
);

CREATE TABLE IF NOT EXISTS "accounts"(
	id INTEGER primary key,
	password TEXT,
	username TEXT,
	email TEXT,
	wishlist TEXT,
	banlist TEXT
);


CREATE TRIGGER update_n_reviews_insert 
AFTER insert
ON reviews
BEGIN
	UPDATE     movies
	SET        n_reviews = (SELECT count(*) from reviews WHERE reviews.movie_id = movies.id);
END;


CREATE TRIGGER update_n_reviews_delete
AFTER delete
ON reviews
BEGIN
	UPDATE     movies
	SET        n_reviews = (SELECT count(*) from reviews WHERE reviews.movie_id = movies.id);
END;

