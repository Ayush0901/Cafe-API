from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import randint
import os

app = Flask(__name__)

##Connect to Database
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///blog.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
API_KEY = "Tw@999#"


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
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route("/random")
def random():
    cafe = Cafe.query.all()
    total = len(cafe)
    random_cafe = Cafe.query.get(randint(0, total))
    # return jsonify(cafe={"can_take_calls": random_cafe.can_take_calls, "coffee_price": random_cafe.coffee_price,
    # "has_sockets": random_cafe.has_sockets, "has_toilets": random_cafe.has_toilet, "has_wifi":
    # random_cafe.has_wifi, "id": random_cafe.id, "img_url": random_cafe.img_url, "location": random_cafe.location,
    # "map_url": random_cafe.map_url, "seats": random_cafe.seats, "name": random_cafe.name})
    #

    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def all():
    all_cafe = Cafe.query.all()
    # cafes = []
    # for cafe in all_cafe:
    #     cafes.append(cafe.to_dict())
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafe])


@app.route("/search")
def search():
    loc = request.args.get("loc")
    all_cafe = Cafe.query.all()
    for cafe in all_cafe:
        print(cafe.location)
        if cafe.location == loc:
            err = False
            print(cafe.location)
            return jsonify(cafe=cafe.to_dict())
    return jsonify(error={"Not Found": "Sorry we could not find any cafe at that location."})


# @app.route('/user/<username>')
# def profile(username):
#     return f'{username}\'s profile'


# HTTP POST - Create Record

@app.route("/add", methods=["POST"])
def add():
    cafe = Cafe(name=request.form.get("name"),
                map_url=request.form.get("map_url"),
                img_url=request.form.get("img_url"),
                location=request.form.get("location"),
                seats=request.form.get("seats"),
                has_toilet=bool(request.form.get("has_toilet")),
                has_wifi=bool(request.form.get("has_wifi")),
                has_sockets=bool(request.form.get("has_sockets")),
                can_take_calls=bool(request.form.get("can_take_calls")),
                coffee_price=request.form.get("coffee_price")
                )
    db.session.add(cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record

@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    all_cafe = Cafe.query.all()
    updated_price = request.args.get("new_price")
    if cafe_id in range(1, len(all_cafe) + 1):
        cafe_to_update = Cafe.query.get(cafe_id)
        cafe_to_update.coffee_price = updated_price
        db.session.commit()
        return jsonify(success="Successfully updated the price"), 200
    else:
        return jsonify(
            error={"Not Found": "Sorry, a cafe with that id was not found in the database. Try again later."}), 404


# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete(cafe_id):
    api_key = request.args.get("api_key")
    all_cafe = Cafe.query.all()
    if cafe_id in range(1, len(all_cafe) + 1):
        if api_key == API_KEY:
            cafe_to_delete = Cafe.query.get(cafe_id)
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(success="Cafe removed from the database successfully"), 200
        else:
            return jsonify(error="Sorry that's not allowed. Make sure you have the correct api_key."), 403
    else:
        return jsonify(
            error={"Not Found": "Sorry a cafe with that id was not found in the database. Try again later."}), 404


if __name__ == '__main__':
    app.run(debug=True)
