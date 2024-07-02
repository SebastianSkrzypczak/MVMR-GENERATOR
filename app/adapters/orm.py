from sqlalchemy import (
    Table,
    MetaData,
    Column,
    Integer,
    String,
    Float,
    Date,
    ForeignKey,
)
from sqlalchemy.orm import registry, clear_mappers
from domain import model
from auth import auth
import config

metadata = MetaData()
mapper_registry = registry(metadata=metadata)


def create_engine():
    engine = config.create_db_engine()
    return engine


destinations = Table(
    "destinations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(255)),
    Column("location", String(255)),
    Column("distance", Float, nullable=False),
)

trips = Table(
    "trips",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "car_id",
        Integer,
        ForeignKey("cars.id", ondelete="CASCADE"),
        nullable=True,
    ),
    Column("date", Date, nullable=False),
    Column(
        "destination_id",
        Integer,
        ForeignKey("destinations.id", ondelete="CASCADE"),
        nullable=True,
    ),
    Column("milage", Float),
)

cars = Table(
    "cars",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("brand", String(255)),
    Column("model", String(255)),
    Column("number_plate", String(16)),
)

refuelings = Table(
    "refuelings",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("date", Date),
    Column("volume", Float),
    Column(
        "car_id",
        Integer,
        ForeignKey("cars.id", ondelete="CASCADE"),
        nullable=True,
    ),
    Column(
        "destination_id",
        Integer,
        ForeignKey("destinations.id", ondelete="CASCADE"),
        nullable=True,
    ),
)

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("login", String(255)),
    Column("password_hash", String(255)),
)


def start_mappers(engine):
    clear_mappers()

    destinations_mapper = mapper_registry.map_imperatively(
        model.Destination, destinations
    )
    cars_mapper = mapper_registry.map_imperatively(model.Car, cars)
    trips_mapper = mapper_registry.map_imperatively(model.Trip, trips)
    refuelings_mapper = mapper_registry.map_imperatively(model.Refueling, refuelings)
    users_mapper = mapper_registry.map_imperatively(auth.User, users)


def main():
    pass


if __name__ == "main":
    main()
