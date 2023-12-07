from adapters import repository
from domain import model
from calendar import monthrange
from datetime import datetime
from icecream import ic
from abc import ABC, abstractmethod


class AbstractMvmr(ABC):
    @abstractmethod
    def add_trip(self):
        pass

    @abstractmethod
    def generete_random(self):
        pass


class Mvmr:
    def __init__(
        self,
        destinations: repository.AbstractRepository,
        refuelings: repository.AbstractRepository,
        month: int,
        year: int,
        current_milage: int,
        previous_milage: int,
        free_days: list[datetime.date] = None,
    ) -> None:
        self.destinations = destinations
        self.refuelings = refuelings
        self.month = month
        self.year = year
        self.free_days = free_days
        self.current_milage = current_milage
        self.previous_milage = previous_milage

        self.available_days = self.get_work_days_in_month()
        self.trips = self.add_refuelings_to_trips()
        self.used_days = []

    def add_trip(
        self, date: datetime, destination: model.Destination, milage: float = 0.0
    ):
        self.trips.append(
            model.Trip(id=0, date=date, destination=destination, milage=milage)
        )

    def remove_days_from_available_days(self, trips: list[model.Trip]):
        self.available_days = [
            day
            for day in self.available_days
            if day not in [trip.date for trip in trips]
        ]

    def get_work_days_in_month(self) -> list[datetime.date]:
        days_in_month = monthrange(self.year, self.month)[1]
        work_days = [
            datetime(self.year, self.month, day).date()
            for day in range(1, days_in_month)
            if datetime(self.year, self.month, day).weekday() not in (6, 7)
        ]
        return work_days
        # TODO: HOLIDAYS API
        # TODO: FREE DAYS

    def add_refuelings_to_trips(self) -> list[model.Trip]:
        refueling_trips = [
            model.Trip(
                id=None,
                date=refueling.date,
                destination=next(
                    destination
                    for destination in self.destinations.content
                    if destination.id == refueling.destination_id
                ),
                milage=None,
            )
            for refueling in self.refuelings.content
            if refueling.date.month == self.month and refueling.date.year == self.year
        ]

        self.remove_days_from_available_days(refueling_trips)
        return refueling_trips

    def generate_random(
        self, previous_milage: float, current_milage: float, **kwargs
    ) -> list[str]:
        set_day_iteration = kwargs.get("set_day_iteration")
        set_trip_iteration = kwargs.get("set_trip_iteration")
        set_factor = kwargs.get("set_factor")
        set_max_difference = kwargs.get("set_max_difference")
