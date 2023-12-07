from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime
from icecream import ic


class Item(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass


@dataclass
class Destination(Item):
    """Class representing one destination."""

    id: int
    name: str
    location: str
    distance: float

    def __str__(self) -> str:
        return f"{self.id}\t{self.name}\t{self.location}\t{self.distance}"


@dataclass
class Trip(Item):
    """Class representing one trip."""

    id: int
    date: datetime
    destination: Destination
    milage: float = 0.0

    def calculate_milage(self, previous_milage: float) -> None:
        self.milage = previous_milage + self.destination.distance

    def __str__(self) -> str:
        return f"{self.id}\t{self.date}\t{self.destination.name}\t{self.destination.distance}\t{self.destination.location}\t{self.milage}"


@dataclass
class Refueling(Item):
    """Class representing one refueling."""

    id: int
    date: datetime
    volume: float
    destination_id: str

    def __str__(self) -> str:
        return f"{self.id}\t{self.date}\t{self.volume}\t{self.destination_id}"
