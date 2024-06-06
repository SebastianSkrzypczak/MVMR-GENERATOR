from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class Item(ABC):
    pass


@dataclass
class Car(Item):

    id: int
    brand: str
    model: str
    number_plate: str

    def __str__(self) -> str:
        return f"{self.id}\t{self.brand}\t{self.model}\t{self.number_plate}"


@dataclass
class Destination(Item):

    id: int
    name: str
    location: str
    distance: float

    def __str__(self) -> str:
        return f"{self.id}\t{self.name}\t{self.location}\t{self.distance}"


@dataclass
class Trip(Item):

    id: int
    date: datetime
    destination: Destination
    car_id: Car
    milage: float = 0.0

    def calculate_milage(self, previous_milage: float) -> None:
        self.milage = previous_milage + self.destination.distance

    # def __str__(self) -> str:
    #     return f"{self.id}\t{self.car_id}\t{self.date}\t{self.destination.name}\t{self.destination.distance}\t{self.destination.location}\t{self.milage}"


@dataclass
class Refueling(Item):

    id: int
    car_id: int
    date: datetime
    volume: float
    destination_id: int

    def __str__(self) -> str:
        return f"{self.id}\t{self.date}\t{self.volume}\t{self.destination_id}"
