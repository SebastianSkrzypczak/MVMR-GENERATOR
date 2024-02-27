from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from services.bootstrap import bootstrap
from services import uow
from adapters import repository
from domain import model
import config
import os

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = config.get_postgres_uri()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

destination_uow, refueling_uow = bootstrap()  # type: uow.AbstractUnitOfWork


# Routes
@app.route("/check_table", methods=["GET"])
def check_table():
    table_name = "destinations"  # Replace with the actual table name you want to check
    table_exists = False

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

    file_path = os.path.join("files", "REFUELINGS.txt")
    with open(file_path, "r") as file:
        refueling_txt_repository = repository.TxtRepository(file, type=model.Refueling)
        refueling_txt_repository.read()
    items = refueling_txt_repository.content
    with refueling_uow:
        for item in items:
            refueling_uow.repository.add(item)
    return jsonify(refueling_uow.repository.content)


@app.route("/destinations", methods=["GET"])
def get_destinations():
    with destination_uow:
        destinations = destination_uow.repository.content
        return jsonify(destinations)


@app.route("/refuelings", methods=["GET"])
def get_refuelings():
    with refueling_uow:
        refuelings = refueling_uow.repository.content
        return jsonify(refuelings)


@app.route("/trips", methods=["GET"])
def get_trips():
    trips = refueling_uow.list()
    result = [
        {
            "id": trip.id,
            "date": trip.date,
            "destination_id": trip.destination_id,
            "milage": trip.milage,
        }
        for trip in trips
    ]
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
