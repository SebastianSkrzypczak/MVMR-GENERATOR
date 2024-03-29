from adapters import repository
from domain import model
from calendar import monthrange
from datetime import datetime
from icecream import ic
from abc import ABC, abstractmethod
import random
from config import get_settings_for_random_generation


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
        destinations: list,
        refuelings: list,
        month: int,
        year: int,
        current_milage: int,
        previous_milage: int,
        car_id: int,
        free_days: list[datetime.date] = None,
    ) -> None:
        self.destinations = destinations
        self.refuelings = refuelings
        self.month = month
        self.year = year
        self.free_days = free_days
        self.previous_milage = previous_milage
        self.range = current_milage - previous_milage
        self.available_days = None
        self.trips = None
        self.car_id = car_id

    def add_trip(
        self, date: datetime, destination: model.Destination, milage: float = 0.0
    ):
        self.trips.append(
            model.Trip(
                id=0,
                car_id=self.car_id,
                date=date,
                destination=destination,
                milage=milage,
            )
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
        self.available_days = work_days
        # TODO: HOLIDAYS API
        # TODO: FREE DAYS

    def add_refuelings_to_trips(self) -> list[model.Trip]:
        refueling_trips = [
            model.Trip(
                id=None,
                date=refueling.date,
                destination=next(
                    destination
                    for destination in self.destinations
                    if destination.id == refueling.destination_id
                ),
                milage=None,
                car_id=self.car_id,
            )
            for refueling in self.refuelings
            if refueling.date.month == self.month and refueling.date.year == self.year
        ]
        for refueling in refueling_trips:
            self.range -= refueling.destination.distance
        self.remove_days_from_available_days(refueling_trips)
        self.trips = refueling_trips

    def renumerate(self):
        last_id = 0
        for trip in self.trips:
            trip.id = last_id + 1
            last_id = trip.id
            trip.milage = self.previous_milage + trip.destination.distance
            self.previous_milage = trip.milage

    def generate_random(self) -> list[str]:
        settings = get_settings_for_random_generation()
        max_difference = settings.get("max_difference")
        while True:
            fitting_destinations = [
                destination
                for destination in self.destinations
                if destination.distance <= self.range
            ]
            if not fitting_destinations:
                break
            if not self.available_days:
                break
            random_date = random.choice(self.available_days)
            random_destination = random.choice(fitting_destinations)
            self.add_trip(random_date, random_destination)
            self.remove_days_from_available_days(self.trips)
            self.range -= random_destination.distance
            if self.range < max_difference:
                break
        self.trips.sort(key=lambda x: getattr(x, "date"))

        self.renumerate()
