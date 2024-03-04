from sqlalchemy import (
    Table,
    MetaData,
    Column,
    Integer,
    String,
    Float,
    Date,
    ForeignKey,
    create_engine,
)
from sqlalchemy.orm import registry, relationship
from config import get_postgres_uri
from domain import model

metadata = MetaData()
mapper_registry = registry(metadata=metadata)
engine = create_engine(get_postgres_uri())

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
    Column("date", Date, nullable=False),
    Column("destination_id", Integer, ForeignKey("destinations.id")),
    Column("milage", Float),
)

refuelings = Table(
    "refuelings",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("date", Date),
    Column("volume", Float),
    Column("destination_id", Integer, ForeignKey("destinations.id")),
)


def start_mappers():
    metadata.create_all(engine)
    destinations_mapper = mapper_registry.map_imperatively(
        model.Destination, destinations
    )
    trips_mapper = mapper_registry.map_imperatively(model.Trip, trips)
    refuelings_mapper = mapper_registry.map_imperatively(model.Refueling, refuelings)
