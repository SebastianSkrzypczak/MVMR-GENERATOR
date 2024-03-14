from flask import Flask, jsonify, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from services.bootstrap import bootstrap
from services import uow, logic
from adapters import repository
from domain import model
from icecream import ic
from datetime import datetime
import os
import config

# import logging

# logging.basicConfig()
# logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = config.get_postgres_uri()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

cars_uow, destination_uow, refueling_uow, trips_uow = (
    bootstrap()
)  # type: uow.AbstractUnitOfWork


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/check_table/<string:table_name>", methods=["GET"])
def check_table(table_name):
    with destination_uow:
        table_exists = destination_uow.table_exist(table_name)

    return jsonify({"table_exists": table_exists})


# @app.route("/load_data", methods=["GET"])
# def load_data():
#     file_path = os.path.join("files", "DESTINATIONS.txt")
#     with open(file_path, "r") as file:
#         destination_txt_repository = repository.TxtRepository(
#             file, type=model.Destination
#         )
#         destination_txt_repository.read()
#     items = destination_txt_repository.content
#     with destination_uow:
#         for item in items:
#             destination_uow.repository.add(item)
#         destination_uow.commit()

#     file_path = os.path.join("files", "REFUELINGS.txt")
#     with open(file_path, "r") as file:
#         refueling_txt_repository = repository.TxtRepository(file, type=model.Refueling)
#         refueling_txt_repository.read()
#     items = refueling_txt_repository.content
#     with refueling_uow:
#         for item in items:
#             refueling_uow.repository.add(item)
#         refueling_uow.commit()
#     return jsonify(refueling_uow.repository.content)


@app.route("/refuelings", methods=["GET", "POST"])
def refuelings():
    if request.method == "POST":
        refuelings_to_delete = request.form.getlist("delete")
        with refueling_uow:
            for destination_id in refuelings_to_delete:
                refueling_uow.repository.remove(int(destination_id))
            refueling_uow.commit()
        return redirect("/refuelings")
    elif request.method == "GET":
        with refueling_uow:
            refuelings = refueling_uow.repository.content
            return render_template("refuelings.html", refuelings=refuelings)


@app.route("/add_destination", methods=["GET", "POST"])
def add_destination():
    if request.method == "POST":
        name = request.form["name"]
        location = request.form["location"]
        distance = request.form["distance"]

        with destination_uow:
            last_id = destination_uow.get_last_id()
            new_destination = model.Destination(last_id + 1, name, location, distance)
            destination_uow.repository.add(new_destination)
            destination_uow.commit()
        return redirect("/destinations")

    return render_template("add_destination.html")


@app.route("/destinations", methods=["GET", "POST"])
def destinations():
    if request.method == "POST":
        destinations_to_delete = request.form.getlist("delete")
        with destination_uow:
            for destination_id in destinations_to_delete:
                destination_uow.repository.remove(int(destination_id))
            destination_uow.commit()
        return redirect("/destinations")
    elif request.method == "GET":
        with destination_uow:
            destinations = destination_uow.repository.content
            return render_template("destinations.html", destinations=destinations)


@app.route("/add_refueling", methods=["GET", "POST"])
def add_refueling():
    if request.method == "POST":
        date = request.form["date"]
        volume = request.form["volume"]
        destination_id = request.form["destination"]
        car_id = request.form["car"]
        with refueling_uow:
            last_id = refueling_uow.get_last_id()
            new_refueling = model.Refueling(
                last_id + 1,
                car_id,
                date,
                volume,
                destination_id,
            )
            refueling_uow.repository.add(new_refueling)
            refueling_uow.commit()
        return redirect("/refuelings")

    with destination_uow:
        destinations = destination_uow.repository.content
    with cars_uow:
        cars = cars_uow.repository.content

    today = datetime.today().strftime("%Y-&m-%d")

    return render_template(
        "add_refueling.html", destinations=destinations, today=today, cars=cars
    )


@app.route("/add_car", methods=["GET", "POST"])
def add_car():
    if request.method == "POST":
        brand = request.form["brand"]
        car_model = request.form["model"]
        number_plate = request.form["number_plate"]

        with cars_uow:
            last_id = cars_uow.get_last_id()
            new_car = model.Car(last_id + 1, brand, car_model, number_plate)
            cars_uow.repository.add(new_car)
            cars_uow.commit()
        return redirect("/cars")

    return render_template("add_car.html")


@app.route("/cars", methods=["GET", "POST"])
def cars():
    if request.method == "POST":
        cars_to_delete = request.form.getlist("delete")
        with cars_uow:
            for car_id in cars_to_delete:
                ic(car_id)
                cars_uow.repository.remove(int(car_id))
            cars_uow.commit()
        return redirect("/cars")

    with cars_uow:
        cars = cars_uow.repository.content
        return render_template("/cars.html", cars=cars)


@app.route("/generate", methods=["GET", "POST"])
def generate():
    if request.method == "POST":
        car_id = int(request.form["car_id"])
        year, month = map(int, request.form["month_year"].split("-"))
        current_milage = int(request.form["current_milage"])
        previous_milage = int(request.form["previous_milage"])
        with destination_uow:
            destinations = destination_uow.repository.content
        with refueling_uow:
            refuelings = refueling_uow.repository.content
        with cars_uow:
            car = cars_uow.repository.find_item(car_id)
        number_plate = car.number_plate
        mvmr = logic.Mvmr(
            destinations, refuelings, month, year, current_milage, previous_milage, car
        )
        mvmr.get_work_days_in_month()
        mvmr.add_refuelings_to_trips()
        mvmr.generate_random()

        return render_template("mvmr.html", trips=mvmr.trips, number_plate=number_plate)
    with cars_uow:
        cars = cars_uow.repository.content
    today = datetime.today().strftime("%m-%d")
    return render_template("generate.html", today=today, cars=cars)


if __name__ == "__main__":
    app.run(debug=True)
