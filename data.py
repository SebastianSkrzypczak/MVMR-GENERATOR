from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Self, TypeVar, Generic
import logging

'''
Module where all classes representing data are located.
There are:
-classes representing single object,
-repositories handling data management,
-classes to handle text files as data storage.
'''

logging.basicConfig(level=logging.DEBUG)
T = TypeVar('T')


@dataclass
class Destination:
    '''Class representing one destination.'''

    id: int
    name: str
    location: str
    distance: float

    def __str__(self) -> str:
        return f'{self.id}\t{self.name}\t{self.location}\t{self.distance}'


@dataclass
class Trip:
    '''Class representing one trip.'''

    id: int
    date: datetime
    destination: Destination
    milage: float = 0

    def __str__(self) -> str:
        return f'{self.id}\t{self.date}\t{self.destination.name}\t{self.destination.distance}\t{self.destination.location}\t{self.milage}'


@dataclass
class Refueling:
    '''Class representing one refueling.'''

    id: int
    date: datetime
    volume: float
    destination: Destination

    def __str__(self) -> str:
        return f'{self.id}\t{self.date}\t{self.volume}\t{self.destination.name}'


class Conversion(Generic[T]):
    '''Generic conversion class for converting data from all kind of sources to objects'''

    date_format = '%Y/%m/%d'

    @abstractmethod
    def convert(self, line: list[str]) -> T:
        return ...


class TripConversion(Conversion[Trip]):

    def convert(self, line: list[str]) -> Trip:
        return Trip(
                    line[0],
                    datetime.strptime(line[1], self.date_format),
                    int(line[2]),  # TODO ID
                    float(line[3])
                   )


class RefuelingConversion(Conversion[Refueling]):

    def convert(self, line: list[str]) -> Refueling:
        return Refueling(
                    0,
                    datetime.strptime(line[0], self.date_format),
                    float(line[1]),
                    int(line[2])  # TODO ID
                   )


class DestinationConversion(Conversion[Destination]):
    def convert(self, line: list[str]) -> Destination:
        return Destination(
                    int(line[0]),
                    line[1],
                    line[2],
                    float(line[3])
                   )


class DataStorage(Generic[T]):
    '''Generic class to manipulate data.'''

    def __init__(self, file, converion: Conversion[T]) -> None:
        self.conversion = converion
        self.file = file

    def open_file(self, mode="r"):
        try:
            return open(self.file, mode, encoding="utf-8")
        except FileNotFoundError as e:
            raise FileNotFoundError(f'File now found error {e}')
        except IOError as error:
            raise IOError(f"File opening error {error}")

    def create(self, new_data) -> None:
        self.read()
        with self.open_file(mode="a") as file:
            file.write(new_data + '\n')

    def read(self) -> list[str]:
        result = []
        with self.open_file() as file:
            output = file.readlines()
        for line in output:
            result.append(self.conversion.convert(line.strip().split('\t')))
        return result

    def update(self, new_data) -> None:
        with self.open_file(mode="w") as file:
            logging.debug(new_data)
            file.write(new_data)

    def delete(self, data_to_delete) -> None:
        pass


class Repository(Generic[T]):
    '''Generic class to represet datasets.'''

    def __init__(self, dataStorage: DataStorage[T]) -> None:
        self.elements: list = None
        self.dataStorage = dataStorage
        self.read()

    def __iter__(self):
        return iter(self.elements)

    def read(self) -> list[T]:
        if self.elements is None:
            self.elements = self.dataStorage.read()

    def add(self, new_element) -> None:
        self.elements.append(new_element)

    def update(self, updated_element) -> None:
        self.elements[updated_element.id] = updated_element

    def delete(self, deleted_element) -> None:
        self.elements.pop(deleted_element.id)
        self.renumerate()

    def renumerate(self) -> None:
        for index, element in enumerate(self.elements):
            element.id = index


destinationsDataStorage = DataStorage('DESTINATIONS.txt', DestinationConversion())
refuelingsDataStorage = DataStorage('REFUELINGS.txt', RefuelingConversion())
tripsDataStorage = DataStorage('TRIPS.txt', TripConversion())
destinations = Repository(destinationsDataStorage)
refuelings = Repository(refuelingsDataStorage)
trips = Repository(tripsDataStorage)
