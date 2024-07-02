from services import logic
from adapters import repository
from domain import model
from datetime import datetime
from icecream import ic
from typing import TextIO


def test_add_refuelings_to_trips():
    refuelings = repository.TxtRepository(TextIO, model.Refueling)
    refuelings.content = [
        model.Refueling("1", 1, datetime(year=2023, month=7, day=2).date(), 50.00, 1),
        model.Refueling("2", 1, datetime(year=2023, month=7, day=10).date(), 52.00, 1),
        model.Refueling("3", 1, datetime(year=2023, month=7, day=24).date(), 48.00, 1),
    ]

    destinations = repository.TxtRepository(TextIO, model.Destination)
    destinations.content = [
        model.Destination("1", "DEST-1", "LOCATION-1", 586.0),
        model.Destination("2", "DEST-2", "LOCATION-2", 434.0),
        model.Destination("3", "DEST-3", "LOCATION-3", 374.0),
    ]
    mvmr = logic.Mvmr(destinations.content, refuelings.content, 7, 2023, 0, 0, 1)
    mvmr.get_work_days_in_month()
    mvmr.add_refuelings_to_trips()
    correct_result = [
        model.Trip(
            None,
            datetime(year=2023, month=7, day=2).date(),
            destinations.content[0],
            1,
            None,
        ),
        model.Trip(
            None,
            datetime(year=2023, month=7, day=10).date(),
            destinations.content[1],
            1,
            None,
        ),
        model.Trip(
            None,
            datetime(year=2023, month=7, day=24).date(),
            destinations.content[2],
            1,
            None,
        ),
    ]
    trips = mvmr.trips
    ic(trips)
    ic(correct_result)

    assert trips == correct_result
