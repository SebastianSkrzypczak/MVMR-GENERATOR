from services import logic
from adapters import repository
from domain import model
from datetime import datetime
from icecream import ic
from typing import TextIO


def test_add_refuelings_to_trips():
    refuelings = repository.TxtRepository(TextIO, model.Refueling)
    refuelings.content = [
        model.Refueling("1", datetime(year=2023, month=7, day=2).date(), 50.00, "1"),
        model.Refueling("2", datetime(year=2023, month=7, day=10).date(), 52.00, "1"),
        model.Refueling("3", datetime(year=2023, month=7, day=24).date(), 48.00, "1"),
    ]

    destinations = repository.TxtRepository(TextIO, model.Destination)
    destinations.content = [
        model.Destination("1", "DEST-1", "LOCATION-1", "586"),
        model.Destination("2", "DEST-2", "LOCATION-2", "434"),
        model.Destination("3", "DEST-3", "LOCATION-3", "374"),
    ]
    mvmr = logic.Mvmr(destinations, refuelings, 7, 2023, 0, 0)
    correct_result = [
        model.Trip(
            None,
            datetime(year=2023, month=7, day=2).date(),
            destinations.content[0],
            None,
        ),
        model.Trip(
            None,
            datetime(year=2023, month=7, day=10).date(),
            destinations.content[0],
            None,
        ),
        model.Trip(
            None,
            datetime(year=2023, month=7, day=24).date(),
            destinations.content[0],
            None,
        ),
    ]
    mvmr.add_refuelings_to_trips()
    trips = mvmr.trips

    assert trips == correct_result
