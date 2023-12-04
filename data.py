from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Self

"""
Module where all classes representing data are located.
There are:
-classes representing single object,
-repositories handling data management,
-classes to handle text files as data storage.
"""


class DataStorage(ABC):
    """Generic class to manipulate data."""

    @abstractmethod
    def create(new_data):
        pass

    @abstractmethod
    def read():
        pass

    @abstractmethod
    def update(old_data, new_data):
        pass

    @abstractmethod
    def delete(data_to_delete):
        pass


@dataclass
class TextFile(DataStorage):
    """Subclass of DataStorage to manipulate data saved in .txt file"""

    file_name: str

    def open_file(self, mode="r"):
        try:
            return open(self.file_name, mode, encoding="utf-8")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File now found error {e}")
        except IOError as error:
            raise IOError(f"File opening error {error}")

    def create(self, new_data) -> None:
        self.read()
        with self.open_file(mode="a") as file:
            file.write(new_data + "\n")

    def read(self) -> list[str]:
        with self.open_file() as file:
            output = file.readlines()
        return output

    def update(self, old_data, new_data) -> None:
        with self.open_file(mode="w") as file:
            file.write(new_data)

    def delete(self, data_to_delete) -> None:
        pass


class Repository(ABC):
    """Generic class to represet datasets."""

    def __init__(self) -> None:
        self.elements_list: list[self.ElementType] = []

    def __iter__(self):
        return iter(self.elements_list)

    def add(self, new_element: "Self.ElementType") -> None:
        self.elements_list.append(new_element)

    def update(self, updated_element: "Self.ElementType") -> None:
        self.elements_list[updated_element.id] = updated_element

    def delete(self, deleted_element: "Self.ElementType") -> None:
        self.elements_list.pop(deleted_element.id)
        self.renumerate()

    def renumerate(self) -> None:
        for index, element in enumerate(self.elements_list):
            element.id = index


@dataclass
class DestinationRepository(Repository):
    """Class to represent all destinations and to manage them."""

    def __init__(self) -> None:
        super().__init__()

    ElementType = Destination


@dataclass
class RefuelingRepository(Repository):
    """Class to represent all refuelings and to manage them."""

    def __init__(self) -> None:
        super().__init__()

    ElementType = Refueling


@dataclass
class TripsRepository(Repository):
    """Class to represent all trips and to manage them."""

    def __init__(self) -> None:
        super().__init__()

    ElementType = Trip


@dataclass
class Conversion(ABC):
    """Generic conversion class for converting data from all kind of sources to objects"""

    @abstractmethod
    def convert(self):
        pass


@dataclass
class DestinationTextFileConversion(Conversion):
    """Class converting data read from file as list of strings to propor objects"""

    destinations_text_file = TextFile("DESTINATIONS.txt")
    destinations: DestinationRepository

    def convert(self) -> None:
        destinations = self.destinations_text_file.read()
        for line in destinations:
            data = line.split("\t")
            id = int(data[0])
            name = data[1]
            location = data[2]
            distance = float(data[3])
            new_destinations = Destination(id, name, location, distance)
            self.destinations.add(new_destinations)


@dataclass
class TripTextFileConversion(Conversion):
    """Class converting data read from file as list of strings to propor objects"""

    trips_text_file = TextFile("TRIPS.txt")
    trips: TripsRepository

    def convert(self) -> None:
        trips = self.trips_text_file.read()
        for line in trips:
            data = line.split("\t")
            id = int(data[0])
            date = datetime(data[1])
            destination_id = int(data[2])
            milage = float(data[3])
            new_trip = Trip(id, date, destination_id, milage)
            self.trips.add(new_trip)


@dataclass
class RefuelingTextFileConversion(Conversion):
    """Class converting data read from file as list of strings to propor objects"""

    refuelings_text_file = TextFile("REFUELINGS.txt")
    refuelings: RefuelingRepository

    def convert(self) -> None:
        refuelings = self.refuelings_text_file.read()
        for line in refuelings:
            data = line.split("\t")
            id = int(data[0])
            date = datetime(data[1])
            volume = float(data[2])
            destination_id = int(data[3])
            new_refueling = Refueling(id, date, volume, destination_id)
            self.refuelings.add(new_refueling)


destinations = DestinationRepository()
refuelings = RefuelingRepository()
trips = TripsRepository()
text_file = TextFile("DESTINATIONS.txt")
output = text_file.read()
conversion = DestinationTextFileConversion(destinations=destinations)
conversion.convert()
