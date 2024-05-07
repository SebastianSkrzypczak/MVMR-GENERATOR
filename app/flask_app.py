from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from services.bootstrap import bootstrap
from services import uow, logic
from adapters import repository
from domain import model
from icecream import ic
from datetime import datetime
from services import manager
import config

# import logging

# logging.basicConfig()
# logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)

app = Flask(__name__)
db_config = config.LocalDbConfiguration

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = str(config.create_db_engine().url)
db = SQLAlchemy(app)

cars_uow, destination_uow, refueling_uow, trips_uow = bootstrap()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/check_table/<string:table_name>", methods=["GET"])
def check_table(table_name):
    with destination_uow:
        table_exists = destination_uow.table_exist(table_name)

    return jsonify({"table_exists": table_exists})


@app.route("/load_data", methods=["GET"])
def load_data():
    destinations_txt_repository = manager.load_data_from_txt_file(
        "DESTINATIONS.txt", model.Destination
    )
    manager.save_data_with_uow(destination_uow, destinations_txt_repository)

    refuelings_txt_repository = manager.load_data_from_txt_file(
        "REFUELINGS.txt", model.Refueling
    )
    manager.save_data_with_uow(refueling_uow, refuelings_txt_repository)

    return jsonify(refueling_uow.repository.content)


def display(
    request,
    modification_function_name: str,
    url_after_removal: str,
    template_name: str,
    uow: uow.AbstractUnitOfWork,
):
    if request.method == "POST":
        if "edit" in request.form:
            id = request.form["edit"]
            return redirect(url_for(modification_function_name, id=id))
        else:
            items_to_delete = request.form.getlist("delete")
            manager.remove_many_with_uow(uow, items_to_delete)
            return redirect(url_after_removal)
    elif request.method == "GET":
        content = manager.get_content_with_uow(uow)
        return render_template(template_name, content=content)


@app.route("/refuelings", methods=["GET", "POST"])
def refuelings():
    return display(
        request=request,
        modification_function_name="modify_refueling",
        url_after_removal="/refuelings",
        template_name="refuelings.html",
        uow=refueling_uow,
    )


@app.route("/destinations", methods=["GET", "POST"])
def destinations():
    return display(
        request=request,
        modification_function_name="modify_destination",
        url_after_removal="/destinations",
        template_name="destinations.html",
        uow=destination_uow,
    )


@app.route("/cars", methods=["GET", "POST"])
def cars():
    ic(manager.get_content_with_uow(cars_uow))
    return display(
        request=request,
        modification_function_name="modify_car",
        url_after_removal="/cars",
        template_name="cars.html",
        uow=cars_uow,
    )


@app.route("/add_refueling", methods=["GET", "POST"])
def add_refueling():
    if request.method == "POST":
        date = datetime.strptime(request.form["date"], "%Y-%m-%d")
        volume = request.form["volume"]
        destination_id = request.form["destination"]
        car_id = request.form["car"]

        last_id = manager.get_last_id_with_uow(refueling_uow)

        new_refueling = model.Refueling(
            last_id + 1, car_id, date, volume, destination_id
        )
        manager.add_with_uow(refueling_uow, new_refueling)

        return redirect("/refuelings")

    cars = manager.get_content_with_uow(cars_uow)
    destinations = manager.get_content_with_uow(destination_uow)
    return render_template("add_refueling.html", cars=cars, destinations=destinations)


@app.route("/add_destination", methods=["GET", "POST"])
def add_destination():
    if request.method == "POST":
        name = request.form["name"]
        location = request.form["location"]
        distance = request.form["distance"]

        last_id = manager.get_last_id_with_uow(destination_uow)
        new_destination = model.Destination(last_id + 1, name, location, distance)
        manager.add_with_uow(destination_uow, new_destination)

        return redirect("/destinations")

    return render_template("add_destination.html")


@app.route("/add_car", methods=["GET", "POST"])
def add_car():
    if request.method == "POST":
        brand = request.form["brand"]
        car_model = request.form["model"]
        number_plate = request.form["number_plate"]

        last_id = manager.get_last_id_with_uow(cars_uow)
        new_car = model.Car(last_id + 1, brand, car_model, number_plate)
        manager.add_with_uow(cars_uow, new_car)

        return redirect("/cars")

    return render_template("add_car.html")


@app.route("/modify_destination/<int:id>", methods=["GET", "POST"])
def modify_destination(id):
    if request.method == "POST":
        name = request.form["name"]
        location = request.form["location"]
        distance = float(request.form["distance"])

        new_destination = model.Destination(id, name, location, distance)
        manager.update_with_uow(destination_uow, id, new_destination)

        return redirect("/destinations")

    return render_template("add_destination.html")


@app.route("/modify_refueling/<int:id>", methods=["GET", "POST"])
def modify_refueling(id):
    if request.method == "POST":
        date = datetime.strptime(request.form["date"], "%Y-%m-%d")
        volume = request.form["volume"]
        destination_id = request.form["destination"]
        car_id = request.form["car"]

        with refueling_uow:
            new_refueling = model.Refueling(
                id,
                car_id,
                date,
                volume,
                destination_id,
            )
            refueling_uow.repository.update(id, new_refueling)
            refueling_uow.commit()
        return redirect("/refuelings")
    with cars_uow:
        cars = cars_uow.repository.content
    with destination_uow:
        destinations = destination_uow.repository.content
    return render_template("add_refueling.html", cars=cars, destinations=destinations)


@app.route("/modify_car/<int:id>", methods=["GET", "POST"])
def modify_car(id):
    if request.method == "POST":
        brand = request.form["brand"]
        car_model = request.form["model"]
        number_plate = request.form["number_plate"]

        new_car = model.Car(id, brand, car_model, number_plate)

        manager.update_with_uow(cars_uow, id, new_car)

        return redirect("/cars")

    return render_template("add_car.html")


def mvmr_factory(car_id, year, month, current_milage, previous_milage):
    with destination_uow:
        destinations = destination_uow.repository.content
    with refueling_uow:
        refuelings = refueling_uow.repository.content
    with cars_uow:
        car = cars_uow.repository.find_item(car_id)

    mvmr = logic.Mvmr(
        destinations, refuelings, month, year, current_milage, previous_milage, car
    )
    return mvmr


def find_car_number_plate(car_id):
    with cars_uow:
        car = cars_uow.repository.find_item(car_id)

    return car.number_plate


@app.route("/generate", methods=["GET", "POST"])
def generate():
    if request.method == "POST":
        car_id = int(request.form["car_id"])
        year, month = map(int, request.form["month_year"].split("-"))
        current_milage = int(request.form["current_milage"])
        previous_milage = int(request.form["previous_milage"])

        mvmr = mvmr_factory(car_id, year, month, current_milage, previous_milage)
        number_plate = find_car_number_plate(car_id)
        mvmr.get_work_days_in_month()
        mvmr.add_refuelings_to_trips()
        mvmr.generate_random()

        return render_template(
            "mvmr.html",
            trips=mvmr.trips,
            number_plate=number_plate,
            year=year,
            month=month,
        )

    with cars_uow:
        cars = cars_uow.repository.content
    today = datetime.today().strftime("%m-%d")
    return render_template("generate.html", today=today, cars=cars)


@app.route("/mvmr", methods=["GET", "POST"])
def mvmr():
    if request.method == "POST":
        pass


if __name__ == "__main__":
    app.run(debug=True)
