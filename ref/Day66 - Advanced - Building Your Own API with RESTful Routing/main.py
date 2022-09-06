import random
from markupsafe import escape
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # __table__為db.Model的一種attribute，可以透過此語法來呼叫出其columns
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
            # 透過getattr()，此python的內建方法，可以取得物件中的該屬性的資料
            # https://www.w3schools.com/python/ref_func_getattr.asp
        return dictionary
        # # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")
    

## HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    cafes = Cafe.query.all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())
    # return jsonify(cafe={ "id":random_cafe.id, "name":random_cafe.name, "map_url":random_cafe.map_url,
    #                "img_url":random_cafe.img_url, "location":random_cafe.location, "seats":random_cafe.seats,
    #                "has_toilet":random_cafe.has_toilet, "has_wifi":random_cafe.has_wifi, "has_sockets":random_cafe.has_sockets,
    #                "can_take_calls":random_cafe.can_take_calls, "coffee_price":random_cafe.coffee_price,})

    # 且jsonify此方法可以彈性調整json資料架構
    # return jsonify(cafe={
    #     # Omit the id from the response
    #     # "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
    #
    #     # Put some properties in a sub-category
    #     "amenities": {
    #         "seats": random_cafe.seats,
    #         "has_toilet": random_cafe.has_toilet,
    #         "has_wifi": random_cafe.has_wifi,
    #         "has_sockets": random_cafe.has_sockets,
    #         "can_take_calls": random_cafe.can_take_calls,
    #         "coffee_price": random_cafe.coffee_price,
    #     }
    # })

@app.route("/all")
def get_all_cafe():
    cafes = Cafe.query.all()
    cafes_list=[i.to_dict() for i in cafes]
    # 將所以db中的物件查詢出來後，將其轉為dict，再存到list中
    # 之後再將其list送到jsonify此方法中
    return jsonify(cafe=cafes_list)

@app.route("/search")
def search_cafe():
    loc = request.args.get("loc")
    # target_cafe=db.session.query(Cafe).filter_by(location=loc).first()
    # 注意，此段需要加上first()的原因，是因為單一地點可能存在多間店家，所以找尋出來的會不只一個物件
    # if target_cafe:
    #     return jsonify(cafe=target_cafes.to_dict())
    # 處理複數，可以透過list comprehension的方式進行to_dict()的轉換
    target_cafes=db.session.query(Cafe).filter_by(location=loc)
    target_cafes=[i.to_dict() for i in target_cafes]
    if target_cafes:
        return jsonify(cafe=target_cafes)
    else:
        return jsonify(error={"Not Found":"Sorry, we don't have a cafe at that location."})

## HTTP POST - Create Record
@app.route("/add",methods=["POST"])
def add_cafe():
    # 在不建立html的情況下，可以直接透過requset.form.get("postman上的變數名稱")
    # 來進行資料的Post
    # 而後透過完整的參數建立，就可以用來進行db的資料新增
    new_cafe=Cafe(
    name = request.form.get("name"),
    map_url = request.form.get("map_url"),
    img_url=request.form.get("img_url"),
    location=request.form.get("loc"),
    has_sockets=bool(request.form.get("sockets")),
    has_toilet=bool(request.form.get("toilet")),
    has_wifi=bool(request.form.get("wifi")),
    can_take_calls=bool(request.form.get("calls")),
    seats=request.form.get("seats"),
    coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"sucess":"Successfully added the new cafe."})


## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>",methods=["PATCH"])
def update_price(cafe_id):
    new_price=request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success":"Successfully updated the price."}),200
        # 透過在jsonify方法的後面，再加上狀態碼，可以將狀態對應到postman的狀態馬上
    else:
        #404 = Resource not found
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}),404


## HTTP DELETE - Delete Record
@app.route("/delete/<int:cafe_id>",methods=["DELETE"])
def delete(cafe_id):
    api_key_answer="KeyAnswer"
    api_key=request.args.get("api_key")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        if api_key==api_key_answer:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success":"Successfully delete the cafe.QQ."}),200
        else:
            return jsonify(error="您ㄉAPI_Key有問題喔"),403
    else:
        return jsonify(error="您所找的資料(id)不存在喔"),404


if __name__ == '__main__':
    app.run(debug=True)
