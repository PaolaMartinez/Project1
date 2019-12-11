CREATE TABLE users (
    username VARCHAR PRIMARY KEY,
    password VARCHAR NOT NULL,
    logged BOOLEAN DEFAULT '0'
    
);

CREATE TABLE books (
    isbn VARCHAR PRIMARY KEY,
    title VARCHAR ,
    author varchar,
    year varchar
);

CREATE TABLE reviews (
    isbn VARCHAR,
    username VARCHAR,
    rating FLOAT ,
    review VARCHAR,
    constraint pk_reviews PRIMARY KEY(isbn, username),
    constraint fk_reviews FOREIGN KEY (isbn) references books(isbn),
    constraint checkRating CHECK (rating >= 1 AND rating <= 5  )

);

SELECT AVG(rating) as avgrating,count(isbn) as numberReviews from reviews where isbn='1416949658' 