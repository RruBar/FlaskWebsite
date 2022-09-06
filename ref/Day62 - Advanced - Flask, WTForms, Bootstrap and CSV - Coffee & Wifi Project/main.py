from flask import Flask, render_template,redirect,url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,SelectField
from wtforms.validators import DataRequired,URL
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)


class CafeForm(FlaskForm):
    cafe = StringField('Cafe name', validators=[DataRequired()])
    url = StringField('Location URL',validators=[DataRequired(),URL()])
    open_time =StringField('Open Time',validators=[DataRequired()])
    close_time=StringField('Close Time',validators=[DataRequired()])
    coffee_rate=SelectField('Coffee Rating', choices=["☕","☕☕","☕☕☕","☕☕☕☕","☕☕☕☕☕"],validators=[DataRequired()])
    wifi_rate = SelectField('Wifi Rating', choices=["✘", "💪", "💪💪", "💪💪💪", "💪💪💪💪", "💪💪💪💪💪"],validators=[DataRequired()])
    power_rate = SelectField('Power Rating', choices=["✘", "🔌", "🔌🔌", "🔌🔌🔌", "🔌🔌🔌🔌", "🔌🔌🔌🔌🔌"],validators=[DataRequired()])
    submit = SubmitField('Submit')



# Exercise:
# add: Location URL, open time, closing time, coffee rating, wifi rating, power outlet rating fields
# make coffee/wifi/power a select element with choice of 0 to 5.
#e.g. You could use emojis ☕️/💪/✘/🔌
# make all fields required except submit
# use a validator to check that the URL field has a URL entered.
# ---------------------------------------------------------------------------


# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add',methods=["GET", "POST"])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        write_data=f"\n{form.cafe.data},{form.url.data},{form.open_time.data}," \
                   f"{form.close_time.data},{form.coffee_rate.data},{form.wifi_rate.data},{form.power_rate.data}"
        with open('cafe-data.csv',mode="a",encoding="utf-8") as file:
            file.write(write_data)
            # 將檔案寫到csv中
        return redirect(url_for('cafes'))
        # 使用redirect進行重新導向，且裡面的使用url_for此方法
    # Exercise:
    # Make the form write a new row into cafe-data.csv
    # with   if form.validate_on_submit()
    return render_template('add.html', form=form)


@app.route('/cafes')
def cafes():
    with open(r'C:\Users\User\Desktop\Re\Python\Udemy\Day62 - Advanced - Flask, WTForms, Bootstrap and CSV - Coffee & Wifi Project\cafe-data.csv', newline='',encoding="utf-8") as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        list_of_rows = []
        for row in csv_data:
            list_of_rows.append(row)
    return render_template('cafes.html', cafes=list_of_rows)


if __name__ == '__main__':
    app.run(debug=True)

