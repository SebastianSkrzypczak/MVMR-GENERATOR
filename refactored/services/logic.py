from adapters import repository
from domain import model
from calendar import monthrange
from datetime import datetime
from icecream import ic


def add_refuelings_to_trips(
    refuelings: repository.AbstractRepository,
    destinations: repository.AbstractRepository,
    month: int,
    year: int,
) -> list[model.Trip]:
    trips = [
        model.Trip(
            id=None,
            date=refueling.date,
            destination=next(
                destination
                for destination in destinations.content
                if destination.id == refueling.destination_id
            ),
            milage=None,
        )
        for refueling in refuelings.content
        if refueling.date.month == month
    ]

    return trips


def generate_mvmr(
    destinations: repository.AbstractRepository,
    refuelings: repository.AbstractRepository,
    previous_milage: float,
    current_milage: float,
    month: int,
    year: int,
    **kwargs
) -> list[str]:
    set_day_iteration = kwargs.get("set_day_iteration")
    set_trip_iteration = kwargs.get("set_trip_iteration")
    set_factor = kwargs.get("set_factor")
    set_max_difference = kwargs.get("set_max_difference")

    range = current_milage - previous_milage
    days_in_month = monthrange[1]

    mvmr = add_refuelings_to_trips(refuelings, destinations, month, year)
