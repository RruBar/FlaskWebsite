from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import os
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
# 讓app包上Bootstrap的風格
Bootstrap(app)

# 建立DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db  =SQLAlchemy(app)

# 建立Movie table
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer,nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    rating = db.Column(db.Float,  nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250),  nullable=True)
    img_url = db.Column(db.String(250),  nullable=False)
    def __repr__(self):
        return f'<Movie: {self.title}>'

if os.path.isfile("movies.db"):
    print("檔案已存在")
else:
    db.create_all()


# 建立
class Update_Form(FlaskForm):
    your_rating = StringField('Your Rating Out of 10 e.g. 7.5', validators=[DataRequired()])
    your_review = StringField('Your Review',validators=[DataRequired()])
    submit = SubmitField('Done')

class Add_Form(FlaskForm):
    movie_title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')


@app.route("/",methods=["GET","POST"])
def home():
    # movies = db.session.query(Movie).all()
    movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(movies)):
        movies[i].ranking = len(movies) - i
    db.session.commit()
    return render_template("index.html",top_10_movie=movies)

@app.route("/find")
def find():
    target_id = request.args.get("id")
    if target_id:
        TMDB_api_key = "f30a88b5594b6a15422a1fa2041f4d7a"
        url=f"https://api.themoviedb.org/3/movie/{target_id}"
        para={"api_key":TMDB_api_key}
        response = requests.get(url,params=para)
        data=response.json()
        new_movie=Movie(
            title=data["title"],
            img_url=f"https://image.tmdb.org/t/p/w500/{data['poster_path']}",
            year=str(data['release_date']).split("-")[0],
            description=data["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('rate_movie',id=new_movie.id))

@app.route('/add',methods=["GET","POST"])
def add():
    add_form = Add_Form()
    if add_form.validate_on_submit():
        adding_movie_name = add_form.movie_title.data
        TMDB_api_key="f30a88b5594b6a15422a1fa2041f4d7a"
        url="https://api.themoviedb.org/3/search/movie"
        para={"api_key":TMDB_api_key,
            "query":adding_movie_name,}
        response = requests.get(url, params=para)
        response.raise_for_status()
        data = response.json()
        query_movie_list_by_dict=data["results"]
        return render_template("select.html",options=query_movie_list_by_dict)
        # for i in data["results"]:
        #     movie_name=i["original_title"]
        #     release_date=i["release_date"]
    return render_template("add.html",form=add_form)


@app.route("/edit",methods=["GET","POST"])
def rate_movie():
    form = Update_Form()
    movie_id = request.args.get("uid")
    target_movie = Movie.query.get(movie_id)
    # 先從資料庫調出這筆資料
    if form.validate_on_submit():
        target_movie.rating=float(form.your_rating.data)
        target_movie.review=form.your_review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html",form=form,movie=target_movie)

@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    target_movie = Movie.query.get(movie_id)
    db.session.delete(target_movie)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
