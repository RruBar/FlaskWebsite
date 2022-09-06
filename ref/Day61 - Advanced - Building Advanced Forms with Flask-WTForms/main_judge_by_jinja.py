from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired,Email,Length,email_validator

app = Flask(__name__)
app.secret_key = "hbr199320xy"
# 在要執行的部分，加上token

class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(),Email()])
    password = PasswordField(label='Password', validators=[DataRequired(),Length(min=8)])
    submit = SubmitField(label='Log in',validators=[DataRequired()] )

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/login", methods=["GET","POST"])
def login():
    login_form=LoginForm()
    if login_form.validate_on_submit():
        if login_form.email.data=="admin@email.com" and login_form.password.data=="12345678":
            return render_template("login.html",form=login_form,submitted=True,credentials=True)
        else:
            return render_template("login.html",form=login_form,submitted=True,credentials=False)
    return render_template("login.html",form=login_form,submitted=False)



if __name__ == '__main__':
    app.run(debug=True)