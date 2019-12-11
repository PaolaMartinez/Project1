import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def read():
    f = open("books.csv")

    data = csv.reader(f)
    return data

def insert(data):
    for isbn, title, author, year in data: 
        db.execute("INSERT INTO books (isbn, title, author, year ) VALUES (:isbn, :title, :author, :year )",
                    {"isbn": isbn, "title": title, "author": author, "year": (year) }) 
        print(f"Added book named {title} with isbn {isbn}, author {author} and year {year}")
    db.commit() # transactions are assumed, so close the transaction finished



def main ():
    data = read()
    insert(data)
    


if (__name__ == "__main__"):
    main() 