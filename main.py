from flask import Flask, jsonify, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from dotenv import load_dotenv
import os
import random

load_dotenv()

app = Flask(__name__)


# CREATE DB
class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URL", "sqlite:///cafes.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record

@app.route("/random")
def get_random_cafe():
    cafe = random.choice(db.session.query(Cafe).all()).to_dict()
    return jsonify(cafe=cafe)


@app.route("/all")
def get_all_cafes():
    cafes = [cafe.to_dict() for cafe in db.session.query(Cafe).all()]
    return jsonify(cafes=cafes)


@app.route("/search")
def find_cafe():
    loc = request.args.get("loc")
    find = db.session.query(Cafe).filter(Cafe.location == loc)
    store = []
    for cafe in find:
        store.append(cafe.to_dict())
    error = {"Not Found": "Sorry, we don't have a cafe at that location."}
    return jsonify(store) if len(store) != 0 else jsonify(error=error)


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add():
    new_cafe = Cafe(
        id=db.session.query(Cafe).count() + 1,
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        seats=request.form.get("seats"),
        has_toilet=request.form.get("toilet") == "True",
        has_wifi=request.form.get("wifi") == "True",
        has_sockets=request.form.get("sockets") == "True",
        can_take_calls=request.form.get("calls") == "True",
        coffee_price=request.form.get("price"))
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record

@app.route('/update-price/<int:cafe_id>', methods=["PATCH"])
def update_price(cafe_id):
    cafe = db.session.get(Cafe, cafe_id)
    if cafe:
        cafe.coffee_price = request.form.get("new_price")
        db.session.commit()
        return jsonify({"success": "Successfully updated the price."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


# HTTP DELETE - Delete Record

@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete(cafe_id):
    if request.form.get("api-key") == "TopSecretAPIKey":
        cafe = db.session.get(Cafe, cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(success={"Success": "Cafe has been successfully removed from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."}), 404
    else:
        return jsonify({"error": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run()
