from flask import Flask, jsonify, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from services.bootstrap import bootstrap
from services import uow
from adapters import repository
from domain import model
from icecream import ic
from datetime import datetime
import os
import config

import logging

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = config.get_postgres_uri()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

destination_uow, refueling_uow = bootstrap()  # type: uow.AbstractUnitOfWork


@app.route("/check_table/<string:table_name>", methods=["GET"])
def check_table(table_name):
    with destination_uow:
        table_exists = destination_uow.table_exist(table_name)

    return jsonify({"table_exists": table_exists})


@app.route("/load_data", methods=["GET"])
def load_data():
    file_path = os.path.join("files", "DESTINATIONS.txt")
    with open(file_path, "r") as file:
        destination_txt_repository = repository.TxtRepository(
            file, type=model.Destination
        )
        destination_txt_repository.read()
    items = destination_txt_repository.content
    with destination_uow:
        for item in items:
            destination_uow.repository.add(item)
        destination_uow.commit()

    file_path = os.path.join("files", "REFUELINGS.txt")
    with open(file_path, "r") as file:
        refueling_txt_repository = repository.TxtRepository(file, type=model.Refueling)
        refueling_txt_repository.read()
    items = refueling_txt_repository.content
    with refueling_uow:
        for item in items:
            refueling_uow.repository.add(item)
        refueling_uow.commit()
    return jsonify(refueling_uow.repository.content)


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

        with refueling_uow:
            last_id = refueling_uow.get_last_id()
            new_refueling = model.Refueling(last_id + 1, date, volume, destination_id)
            refueling_uow.repository.add(new_refueling)
            refueling_uow.commit()
        return redirect("/refuelings")

    with destination_uow:
        destinations = destination_uow.repository.content

    today = datetime.today().strftime("%Y-&m-%d")

    return render_template("add_refueling.html", destinations=destinations, today=today)


if __name__ == "__main__":
    app.run(debug=True)
