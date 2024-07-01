from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from services.bootstrap import bootstrap
from services import uow, logic, manager
from domain import model
from datetime import datetime, timedelta
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from auth import auth
from icecream import ic
import config

app = Flask(__name__)
app.secret_key = "sadasoasdj111sad"  # config.get_app_secret_key()
login_manager = LoginManager()

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = str(config.create_db_engine().url)
app.config["PERMAMENT_SESSION_LIFTIME"] = timedelta(minutes=30)
db = SQLAlchemy(app)

login_manager.init_app(app)

cars_uow, destination_uow, refueling_uow, trips_uow, users_uow = bootstrap()


@login_manager.user_loader
def load_user(user_id):
    return manager.find_item_by_id_with_uow(users_uow, int(user_id))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = manager.authenicate_user(users_uow, username, password)
        if user:
            login_user(user)
            return redirect(url_for("index"))
        return "Invalid credentials"
    return render_template("login.html")


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        id = manager.get_last_id_with_uow(users_uow)
        user = auth.User(id + 1, username)
        user.set_password(password)

        manager.add_with_uow(users_uow, user)
        return redirect(url_for("login"))
    return render_template("register.html")


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for("login"))


@app.route("/", methods=["GET"])
@login_required
def index():
    username = current_user.login
    return render_template("index.html", username=username)


@app.route("/load_data", methods=["GET"])
@login_required
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
        ic(content)
        return render_template(template_name, content=content)


@app.route("/refuelings", methods=["GET", "POST"])
@login_required
def refuelings():
    return display(
        request=request,
        modification_function_name="modify_refueling",
        url_after_removal="/refuelings",
        template_name="refuelings.html",
        uow=refueling_uow,
    )


@app.route("/destinations", methods=["GET", "POST"])
@login_required
def destinations():
    return display(
        request=request,
        modification_function_name="modify_destination",
        url_after_removal="/destinations",
        template_name="destinations.html",
        uow=destination_uow,
    )


@app.route("/cars", methods=["GET", "POST"])
@login_required
def cars():
    return display(
        request=request,
        modification_function_name="modify_car",
        url_after_removal="/cars",
        template_name="cars.html",
        uow=cars_uow,
    )


@app.route("/trips", methods=["GET", "POST"])
@login_required
def trips():
    return display(
        request=request,
        modification_function_name=None,
        url_after_removal="/trips",
        template_name="trips.html",
        uow=trips_uow,
    )


@app.route("/add_refueling", methods=["GET", "POST"])
@login_required
def add_refueling():
    if request.method == "POST":
        date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
        volume = float(request.form["volume"])
        destination_id = request.form["destination"]
        car_id = int(request.form["car"])

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
@login_required
def add_destination():
    if request.method == "POST":
        name = request.form["name"]
        location = request.form["location"]
        distance = float(request.form["distance"])

        last_id = manager.get_last_id_with_uow(destination_uow)
        new_destination = model.Destination(last_id + 1, name, location, distance)
        manager.add_with_uow(destination_uow, new_destination)

        return redirect("/destinations")

    return render_template("add_destination.html")


@app.route("/add_car", methods=["GET", "POST"])
@login_required
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


@app.route("/add_trip", methods=["GET", "POST"])
@login_required
def add_trip():
    if request.method == "POST":
        print(request.form)
        date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
        destination_id = int(request.form["destination"])
        car_id = request.form["car"]
        ic(car_id)
        destination = manager.find_item_by_id_with_uow(destination_uow, destination_id)
        last_id = manager.get_last_id_with_uow(trips_uow)
        new_trip = model.Trip(last_id + 1, date, destination, car_id, milage=0)
        ic(new_trip)

        manager.add_with_uow(trips_uow, new_trip)

        return redirect("/trips")

    cars = manager.get_content_with_uow(cars_uow)
    destinations = manager.get_content_with_uow(destination_uow)
    return render_template("add_trip.html", cars=cars, destinations=destinations)


@app.route("/modify_destination/<int:id>", methods=["GET", "POST"])
@login_required
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
@login_required
def modify_refueling(id):
    if request.method == "POST":
        date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
        volume = float(request.form["volume"])
        destination_id = int(request.form["destination"])
        car_id = int(request.form["car"])

        new_refueling = model.Refueling(
            id,
            car_id,
            date,
            volume,
            destination_id,
        )

        manager.update_with_uow(refueling_uow, id, new_refueling)

        return redirect("/refuelings")

    cars = manager.get_content_with_uow(cars_uow)
    destinations = manager.get_content_with_uow(destination_uow)

    return render_template("add_refueling.html", cars=cars, destinations=destinations)


@app.route("/modify_car/<int:id>", methods=["GET", "POST"])
@login_required
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
    destinations = manager.get_content_with_uow(destination_uow)
    refuelings = manager.get_content_with_uow(refueling_uow)
    car = manager.find_item_by_id_with_uow(cars_uow, car_id)

    mvmr = logic.Mvmr(
        destinations, refuelings, month, year, current_milage, previous_milage, car
    )
    return mvmr


def find_car_number_plate(car_id):
    with cars_uow:
        car = cars_uow.repository.find_item(car_id)

    return car.number_plate


@app.route("/generate", methods=["GET", "POST"])
@login_required
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
            previous_milage=previous_milage,
            trips=mvmr.trips,
            number_plate=number_plate,
            year=year,
            month=month,
        )

    cars = manager.get_content_with_uow(cars_uow)
    today = datetime.today().strftime("%m-%d")

    return render_template("generate.html", today=today, cars=cars)


if __name__ == "__main__":
    app.run(debug=True)
