import os
import requests
from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return  render_template("index.html")


@app.route("/welcome")
def welcome():
    name = request.form.get("name") # take the request the user made, access the form,
                                    # and store the field called `name` in a Python variable also called `name`
    return render_template("form.html", name=name)


@app.route("/register", methods=["POST"])
def register():
    """Register new user"""

    # Get form information.
    username = request.form.get("username")
    password = request.form.get("password")
      
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount > 0:
        return "User exists already"
    db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
            {"username": username, "password": password})
    db.commit()
    return render_template("success.html")

@app.route("/login", methods=["POST"])
def login():
    # Login of users
    # Get form information.
    username = request.form.get("username")
    password = request.form.get("password")
      
    if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).rowcount > 0:
        db.execute("UPDATE users SET logged = '1' WHERE username = :username AND password = :password", {"username": username, "password": password})
        db.commit()
        session["up"] = []
        session["up"].append(username)
        session["up"].append(password)
        return redirect(url_for('search'))

    return "Password or user incorrect."

@app.route("/logout")
def logout():
    username = session["up"][0]
    password = session["up"][1]
      
    db.execute("UPDATE users SET logged = '0' WHERE username = :username AND password = :password", {"username": username, "password": password})
    db.commit()


    return redirect(url_for('index'))


@app.route("/review_sub/<string:ISBN>", methods=["POST"])
def review_submission(ISBN):
    username = session["up"][0]
    isbn = ISBN
    
    rating = request.form.get("rating")
    review = request.form.get("review")
    if db.execute("SELECT * FROM reviews WHERE username = :username AND isbn = :isbn", {"username": username, "isbn": isbn}).rowcount == 0:
        db.execute("INSERT INTO reviews (isbn, username, rating, review) VALUES (:isbn, :username, :rating, :review)",
            {"username": username, "isbn": isbn, "rating": rating, "review":review})
        db.commit()
        return render_template('review_sub.html', message="New review created", isbn=isbn) 
    else:
        db.execute("UPDATE reviews SET rating = :rating, review = :review WHERE username = :username AND isbn = :isbn", {"username": username, "isbn": isbn, "rating": rating, "review":review})
        db.commit()
        return render_template('review_sub.html', message="Your review has been updated. Remember you cannot make two reviews of the same book.", isbn=isbn)

@app.route("/review/<string:ISBN>", methods = ["GET"])
def get_reviews(ISBN):
    isbn = ISBN
    return render_template("review.html", isbn = isbn)

@app.route("/search", methods = ["GET","POST"])
def search():
    results = 0
    if request.method ==  "POST":     
        search_data = request.form.get("search_data")
        results = query_for_search(search_data)

    return render_template("search.html", results = results)

@app.route("/search/<string:isbn>", methods = ["GET"])
def search_book(isbn):
    book, reviews = books_and_reviews_query(isbn)
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "vUtj0q1riaKu3LxMuf7dwA", "isbns": isbn})
    if len(book) == 0:
        return render_template('404.html'), 404
    return render_template("books.html", book = book[0], reviews = reviews, isbn = isbn, res = res.json()['books'][0])

@app.route("/api/<string:isbn>", methods = ["GET"])
def get_api(isbn):

    book, reviews = books_and_reviews_query(isbn)

    if len(book) == 0:
        return render_template('404.html'), 404
    else :
        book = book[0]
        json_res = {
        "title": book.title,
        "author": book.author,
        "year": int(book.year),
        "isbn": book.isbn,
        "review_count": len(reviews),
        "average_score": rating_cal(reviews)
        }
        return jsonify(json_res), 200



def query_for_search(str):
      data = db.execute("SELECT * FROM books WHERE title LIKE '%"+str+"%' or  author LIKE '%"+str+"%' or  isbn LIKE '%"+str+"%';").fetchall()
      return data

def books_and_reviews_query(str):
      book = db.execute("SELECT * FROM books WHERE isbn = '"+str+"';").fetchall()
      reviews = db.execute("SELECT * FROM reviews WHERE isbn = '"+str+"';").fetchall()
      return book, reviews

def rating_cal(reviews):
    if len(reviews) > 0:
        rating = 0
        for review in reviews :
            rating += review.rating
        rating = rating / len(reviews)
        return rating
    else:
        return 0
