from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import datetime


## Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['CKEDITOR_PKG_TYPE'] = 'basic'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])

    body = CKEditorField("Blog Content", validators=[DataRequired()])
    # 若wtf要套用CKEditor的模板，在import時注意from flask_ckeditor import CKEditor, CKEditorField

    submit = SubmitField("Submit Post")



# all_posts=db.session.query(BlogPost).all()
# posts=[i for i in all_posts]
# all_posts=all_posts[:3]


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)

# 透過DB資料渲染網頁
@app.route("/post/<int:post_id>")
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    return render_template("post.html", post=requested_post)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post",methods=["GET","POST"])
def create_new_post():
    post_form = CreatePostForm()
    if post_form.validate_on_submit():
        now = datetime.now()
        new_post = BlogPost(title=post_form.title.data,subtitle=post_form.subtitle.data,
                            date=f'{now.strftime("%B")}{now.strftime("%d")},{now.strftime("%Y")}',
                            body=post_form.body.data,author=post_form.author.data,img_url=post_form.img_url.data,
                            )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html",form=post_form, new_post=True)

@app.route("/edit_post/<int:post_id>",methods=["GET","POST"])
def edit_post(post_id):
    target_post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(title=target_post.title,subtitle=target_post.subtitle,
                               author=target_post.author,img_url=target_post.img_url,body=target_post.body)
    if edit_form.validate_on_submit():
        target_post.title=edit_form.title.data
        target_post.subtitle=edit_form.subtitle.data
        target_post.author=edit_form.author.data
        target_post.img_url=edit_form.img_url.data
        target_post.body=edit_form.body.data
        db.session.commit()
        return redirect(url_for('show_post',post_id=target_post.id))
    return render_template("make-post.html",form=edit_form, new_post=False)

@app.route("/delete/<int:post_id>",methods=["GET","POST"])
def delete_post(post_id):
    target_post = BlogPost.query.get(post_id)
    db.session.delete(target_post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
