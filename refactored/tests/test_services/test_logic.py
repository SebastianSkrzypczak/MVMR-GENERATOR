from services import logic
from adapters import repository
from domain import model
from datetime import datetime
from icecream import ic
from typing import TextIO


def test_add_refuelings_to_trips():
    refuelings = repository.TxtRepository(TextIO, model.Refueling)
    refuelings.content = [
        model.Refueling("1", datetime(year=2023, month=7, day=2), 50.00, "1"),
        model.Refueling("2", datetime(year=2023, month=7, day=10), 52.00, "1"),
        model.Refueling("3", datetime(year=2023, month=7, day=24), 48.00, "1"),
    ]

    destinations = repository.TxtRepository(TextIO, model.Destination)
    destinations.content = [
        model.Destination("1", "DEST-1", "LOCATION-1", "586"),
        model.Destination("2", "DEST-2", "LOCATION-2", "434"),
        model.Destination("3", "DEST-3", "LOCATION-3", "374"),
    ]
    correct_result = [
        model.Trip(
            None, datetime(year=2023, month=7, day=2), destinations.content[0], None
        ),
        model.Trip(
            None, datetime(year=2023, month=7, day=10), destinations.content[0], None
        ),
        model.Trip(
            None, datetime(year=2023, month=7, day=24), destinations.content[0], None
        ),
    ]

    trips = logic.add_refuelings_to_trips(refuelings, destinations, 7, 2023)
    ic(trips)
    ic(correct_result)
    assert trips == correct_result
