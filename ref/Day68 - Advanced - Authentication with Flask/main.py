from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
# 會需要設置app_secret_key的原因，是因為當flask要使用要session或者其他flask的衍生套件(如WTForm，要避免CSRF攻擊)，
# 需要有secret key來進行加密
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# 設置SQLALCHEMY的db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flask_Login
login_manger = LoginManager()
login_manger.init_app(app)
# 將 flask 和 Flask-Login 綁定起來。
# 透過此設置，可以讓Flask-Login uses sessions for authentication

@login_manger.user_loader
#
def load_user(user_id):
    return User.query.get(int(user_id))


##CREATE TABLE IN DB
# 透過讓User繼承UserMixin，可以讓該class取得is_authenticated、is_active、is_anonymous這些屬性以及get_id()此方法
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
#Line below only required once, when creating DB. 
# db.create_all()







@app.route('/')
def home():
    return render_template("index.html",logged_in=current_user.is_authenticated)


@app.route('/register',methods=["GET","POST"])
def register():
    if request.method=="POST":
        email=request.form.get("email")
        # 透過email來調取資料庫資料
        if User.query.filter_by(email=email).first():
            flash('該Email已經存在，換一個吧')
            return redirect(url_for('login'))
        new_user=User()
        new_user.name=request.form.get("name")
        new_user.email=request.form.get("email")
        new_user.password=generate_password_hash(password=request.form.get("password"),method='pbkdf2:sha256',salt_length=8)
        db.session.add(new_user)
        db.session.commit()

        # 完成資料新增後，將user轉為登入且認證狀態，透過login_user此方法來記錄使用者資料
        # Log in and authenticate user after adding details to database.
        login_user(new_user)

        return redirect(url_for("secrets"))

    return render_template("register.html",logged_in=current_user.is_authenticated)


@app.route('/login',methods=["POST","GET"])
def login():
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")
        # 透過email來調取資料庫資料
        user_data=User.query.filter_by(email=email).first()
        if not user_data:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # 密碼錯誤
        elif not check_password_hash(user_data.password,password):
            # check_password_hash(a,b) a要擺hash值，b則是擺要被hash來進行比較的值
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user_data)
            # return render_template("secrets.html",user=user_data)
            return redirect(url_for('secrets'))
    return render_template("login.html",logged_in=current_user.is_authenticated)


@app.route('/secrets')
@login_required
# 此頁面套上需要登入後才出現
def secrets():
    print(current_user.name)
    return render_template("secrets.html",user=current_user.name,logged_in=True)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download/<path:filename>')
@login_required
def download(filename):
    # 打開檔案透過send_from_directory，設定好資料夾以及路徑
    # flask.send_from_directory(directory, path, **kwargs)
    return send_from_directory('static', filename)


if __name__ == "__main__":
    app.run(debug=True)
