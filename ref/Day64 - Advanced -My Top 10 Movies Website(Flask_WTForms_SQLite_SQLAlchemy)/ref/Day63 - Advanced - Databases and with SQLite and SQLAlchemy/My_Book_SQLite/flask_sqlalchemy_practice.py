from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# Create Database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///new-books-collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db  =SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    author = db.Column(db.String(250),unique=True)
    rating = db.Column(db.Float, unique=True, nullable=False)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return '<Book %r>' % self.title
        # 將物件的資訊可以將其title直接呈現出來
        # 但同樣可以透過object.title、object.author來呼叫相關屬性資訊

# db.create_all()
# 透過此語法.create_all()來建立db

# Create item
# new_book = Book(id=1,title="Harry Potter",author="J.K. Rowling", rating=9.3)
# #其實也可以不用寫id，因為id本身是primary key，本身會進行 auto-generated
# new_book = Book(title="RRRRRRR",author="AAAAAAAAAA", rating=8.7)
# db.session.add(new_book)
# db.session.commit()

# All Records，兩種查資料方式
all_books = db.session.query(Book).all()
all_books_2 =  Book.query.all()
print(all_books)
print(all_books_2)

# Read A Particular Record By Query
book_1 = Book.query.filter_by(title="RRRRRRR").first()
book_2 = Book.query.filter_by(author="AAAAAAAAAA").first()
book_3 = Book.query.filter_by(id=1).first()
# 透過filter_by，可以針對屬性進行物件的篩選
print(book_1.author)
print(book_2)
print(book_3)

# # Update A Particular Record By Query
# book_to_update = Book.query.filter_by(title="Harry Potter").first()
# book_to_update.title = "Harry Potter and the Chamber of Secrets"
# db.session.commit()

# # Update A Record By PRIMARY KEY
# book_id = 1
# book_to_update = Book.query.get(book_id)
# # query.get看起來是直接透過ID來抓取，而非使用filter進行屬性上的篩選(或許為id的特別用法)
# book_to_update.title = "Harry Potter and the Goblet of Fire"
# db.session.commit()


# Delete A Particular Record By PRIMARY KEY
# book_id = 1
# book_to_delete = Book.query.get(book_id)
# db.session.delete(book_to_delete)
# db.session.commit()