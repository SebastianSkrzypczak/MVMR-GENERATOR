from flask import Flask, jsonify, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from services.bootstrap import bootstrap
from services import uow
from adapters import repository
from domain import model
import config


# import logging

# logging.basicConfig()
# logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)

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

#     file_path = os.path.join("files", "REFUELINGS.txt")
#     with open(file_path, "r") as file:
#         refueling_txt_repository = repository.TxtRepository(file, type=model.Refueling)
#         refueling_txt_repository.read()
#     items = refueling_txt_repository.content
#     with refueling_uow:
#         for item in items:
#             refueling_uow.repository.add(item)
#     return jsonify(refueling_uow.repository.content)


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
            return redirect("/destinations_list")

    return render_template("add_destination.html")


@app.route("/destinations_list", methods=["GET", "POST"])
def destinations_list():
    if request.method == "POST":
        destinations_to_delete = request.form.getlist("delete")
        with destination_uow:
            for destination_id in destinations_to_delete:
                destination_uow.repository.remove(int(destination_id))
            destination_uow.commit()
        return redirect("/destinations_list")
    elif request.method == "GET":
        with destination_uow:
            destinations = destination_uow.repository.content
            return render_template("destinations_list.html", destinations=destinations)


if __name__ == "__main__":
    app.run(debug=True)
