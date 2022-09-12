"""
可透過pip install pipreqs
# 在當前目錄生成req文件
pipreqs. - -encoding = utf8 - -force
"""
import datetime,os
import smtplib,requests
import flask
from flask import Flask, render_template, redirect, url_for, flash,abort
from web_form import RegisterForm,LoginForm,CreatePostForm,CommentForm
from functools import wraps
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_gravatar import Gravatar #　Gravatar功能用來提供comment時的頭像用

import ssl #  SSL  處理，  https    SSSSSS 就需要加上以下2行
ssl._create_default_https_context = ssl._create_unverified_context    # 因.urlopen發生問題，將ssl憑證排除


app = Flask(__name__,static_url_path='/static')
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///personal_web.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manger = LoginManager()
login_manger.init_app(app)

@login_manger.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 個人網站相關Table
class User(UserMixin,db.Model):
    __tablename__="users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250),nullable=False)
    email = db.Column(db.String(250),unique=True,nullable=False)
    password = db.Column(db.String(250),nullable=False)
    #This will act like a List of BlogPost objects attached to each User.
    #The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost",back_populates="author")
    comments = relationship("Comment",back_populates='comment_author')

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    # 透過__tablename__來進行該表命名
    id = db.Column(db.Integer, primary_key=True)
    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    # 透過抓取
    author_id=db.Column(db.Integer, db.ForeignKey('users.id'))
    #Create reference to the User object, the "posts" refers to the posts protperty in the User class.
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    comments = relationship("Comment",back_populates='parent_post')

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post=relationship("BlogPost",back_populates="comments")
    text=db.Column(db.Text, nullable=False)


db.create_all()

def admin_only(fun):
    @wraps(fun)
    def decorated_fun(*args, **kwargs):
        # 如果使用者ID不等於1，顯示403error
        if current_user.id !=1:
            return abort(403)
        return fun(*args, **kwargs)
    return decorated_fun


weather_url="https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=rdec-key-123-45678-011121314"
def get_weather(url:str):
    response = requests.get(url)
    data=response.json()
    data=data["records"]["location"]
    cols=["縣市","現在天氣","氣溫","降雨機率"]
    results=[]
    for i in data:
        now_weather=i["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
        low_temp=i["weatherElement"][2]["time"][0]["parameter"]["parameterName"]
        high_temp=i["weatherElement"][4]["time"][0]["parameter"]["parameterName"]
        rain_percent=i["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
        results.append([i["locationName"],now_weather,f"{low_temp}~{high_temp}度",f"{rain_percent}%"])
    return cols,results

@app.route("/")
def home():
    #TODO 首頁的天氣API資料抓取待修條件
    try:
        cols,results=get_weather(weather_url)
    except:
        cols,results=None,None
    index_dict={
        "首頁開頭":"Hi，我叫何柏融，歡迎來到我的個人網站逛逛<br>既然都來了不訪再多看看我的作品😀",
        "聯繫信箱":" hbr199320xy@gmail.com",
        "自我介紹開頭":"關於<strong>我</strong>的事情<br>你/妳可以先知道的是",
        "自我介紹內文":"<h3>目前技能大致大概如下<h3><br>"
                 "<h3><strong style='color:black'>Python:</strong></h3>"
                 "<ul>"
                 "<li>Flask及相關工具(SQLAlchemy 、WTForm)</li>"
                 "<li>爬蟲相關套件(bs4、selenium)</li>"
                 "<li>API串接(如Line Bot)</li>"
                 "<li>GUI相關工具(Tkinter)</li>"
                 "</ul>"
                 "<h3><strong style='color:black'>Html/Css:</strong></h3>基礎架構調整以及Bootstrap模板套用<br>"
                 "<h3><strong style='color:black'>MySQL:</strong></h3>基礎CRUD(可參考作品影片)",
    }
    return render_template("index.html",index=index_dict,cols=cols,results=results,locate_index=True,current_user=current_user)

@app.route('/register',methods=["POST","GET"])
def register():
    register_form=RegisterForm()
    if register_form.validate_on_submit():
        email=register_form.email.data
        user_data = User.query.filter_by(email=email).first()
        if user_data:
            flash("這個信箱已經註冊過了，你要不要登入看看?")
            return redirect(url_for('login'))
        else:
            # pass
            hash_password=generate_password_hash(register_form.password.data,method='pbkdf2:sha256',salt_length=8)
            new_user=User(name=register_form.name.data,
                          email=register_form.email.data,
                          password=hash_password)
            # 在召喚新物件時，已經選定好class(db.table)了
            db.session.add(new_user)
            db.session.commit()
            # 註冊即完成認證
            login_user(new_user)
            return redirect(url_for('home'))
    return render_template('register.html',form=register_form,current_user=current_user)

@app.route('/login',methods=["POST","GET"])
def login():
    loginform=LoginForm()
    if loginform.validate_on_submit():
        email=loginform.email.data
        user_data=User.query.filter_by(email=email).first()
        if not user_data:
            flash("查無此信箱(帳號)")
            return redirect(url_for('login'))
        elif not check_password_hash(user_data.password,loginform.password.data):
            flash("密碼錯誤")
            return redirect(url_for('login'))
        else:
            login_user(user_data)
            return redirect(url_for('home'))
    return render_template("login.html",form=loginform,current_user=current_user)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))



@app.route("/contact",methods=["GET","POST"])
def contact():
    if flask.request.method == "POST":
        if not current_user.is_authenticated:
            name=flask.request.form['name']
            email=flask.request.form['email']
        else:
            name=current_user.name
            email=current_user.email
        message=flask.request.form['message']
        my_email = "hbr199320xy@gmail.com"
        password = os.environ.get('gmail_password')
        with smtplib.SMTP_SSL("smtp.gmail.com",timeout=120) as connect:
            connect.login(user=my_email,password=password)
            connect.sendmail(from_addr=my_email,
                             to_addrs=my_email,
                             msg=f"Subject:有人寄信給你囉~\n\n"
                                 f"留訊者:{name}\nE-mail:{email}\n"
                                 f"留言內容:{message}".encode("utf-8"))
        return flask.render_template("contact.html",msg_sent=True,locate_index=False)
    return flask.render_template("contact.html",msg_sent=False,locate_index=False)

@app.route("/blog")
def blog():
    posts = BlogPost.query.all()
    posts.reverse()
    print(posts)
    # 今天筆數<=1筆時，只顯示
    if len(posts)==0:
        posts=False
        return flask.render_template("blog.html", locate_index=False, all_posts=posts)
    else:
        return flask.render_template("blog.html",locate_index=False,all_posts=posts)

@app.route("/new-post",methods=["POST","GET"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("blog"))
    return render_template("make-post.html", form=form,current_user=current_user)

@app.route("/edit-post/<int:post_id>",methods=["POST","GET"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("blog", post_id=post.id))

    return render_template("make-post.html", form=edit_form,current_user=current_user)



gravatar = Gravatar(app,size=100, rating='g', default='retro', force_default=False, force_lower=False)


@app.route("/post-detail/<int:post_id>",methods=["GET","POST"])
def blog_detail(post_id):
    requested_post = BlogPost.query.get(post_id)
    form = CommentForm()
    comment_content = form.body.data
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("您尚未註冊or登入")
            return redirect(url_for('login'))
        new_comment = Comment(text=comment_content, comment_author=current_user, parent_post=requested_post)
        db.session.add(new_comment)
        db.session.commit()
    return render_template("post-detail.html", post=requested_post, current_user=current_user, form=form,locate_index=False)

    # html_blog_detail=flask.render_template("blog-detail.html",locate_index=False)
    # return html_blog_detail

@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/project-detail")
def project_detail():
    html_project_detail=flask.render_template("project-detail.html",locate_index=False)
    return html_project_detail



if __name__ == '__main__':
   app.run(port=8080,debug=True,host='0.0.0.0')
