from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Self


class DataStorage(ABC):
    '''Generic class to manipulate data.'''

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

    def calculate_milage(self, current_milage) -> None:
        pass

    def __str__(self) -> str:
        return f'{self.id}\t{self.date}\t{self.destination.name}\t{self.destination.distance}\t{self.destination.location}\t{self.milage}'


@dataclass
class Refueling:
    '''Class representing one refueling.'''
    id: int
    date: datetime
    volume: float
    destination_id: int

    def __str__(self) -> str:
        return f'{self.id}\t{self.date}\t{self.volume}\t{self.destination.name}'


@dataclass
class TextFile(DataStorage):
    ''' Subclass of DataStorage to manipulate data saved in .txt file'''
    file_name: str

    def open_file(self, mode="r"):
        try:
            return open(self.file_name, mode, encoding="utf-8")
        except FileNotFoundError as e:
            raise FileNotFoundError(f'File now found error {e}')
        except IOError as e:
            raise IOError(f"File opening error {e}")

    def create(self, new_data) -> None:
        self.read()
        with self.open_file(mode="a") as file:
            file.write(new_data + '\n') 

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
    '''Generic class to represet datasets.'''

    def __init__(self) -> None:
        self.elements_list: list[self.ElementType] = []

    def add(self, new_element: 'Self.ElementType') -> None:
        self.elements_list.append(new_element)

    def update(self, updated_element: 'Self.ElementType') -> None:
        self.elements_list[updated_element.id] = updated_element

    def delete(self, deleted_element: 'Self.ElementType') -> None:
        self.elements_list.pop(deleted_element.id)
        self.renumerate()

    def renumerate(self) -> None:
        for index, element in enumerate(self.elements_list):
            element.id = index


@dataclass
class DestinationRepository(Repository):
    '''Class to represent all destinations and to manage them.'''
    def __init__(self) -> None:
        super().__init__()

    ElementType = Destination


@dataclass
class RefuelingRepository(Repository):
    '''Class to represent all refuelings and to manage them.'''
    def __init__(self) -> None:
        super().__init__()

    ElementType = Refueling


@dataclass
class TripsRepository(Repository):
    '''Class to represent all trips and to manage them.'''
    def __init__(self) -> None:
        super().__init__()

    ElementType = Trip


@dataclass
class Conversion(ABC):
    '''Generic conversion class for converting data from all kind of sources to objects'''

    @abstractmethod
    def convert(self):
        pass


@dataclass
class DestinationTextFileConversion(Conversion):
    '''Class converting data read from file as list of strings to propor objects'''

    destinations_text_file = TextFile("DESTINATIONS.txt")
    destinations: DestinationRepository

    def convert(self) -> None:
        destinations = self.destinations_text_file.read()
        for line in destinations:
            data = line.split('\t')
            id = int(data[0])
            name = data[1]
            location = data[2]
            distance = float(data[3])
            new_destinations = Destination(id, name, location, distance)
            self.destinations.add(new_destinations)


@dataclass
class TripTextFileConversion(Conversion):
    '''Class converting data read from file as list of strings to propor objects'''

    trips_text_file = TextFile("TRIPS.txt")
    trips: TripsRepository

    def convert(self) -> None:
        trips = self.trips_text_file.read()
        for line in trips:
            data = line.split('\t')
            id = int(data[0])
            date = datetime(data[1])
            destination_id = int(data[2])
            milage = float(data[3])
            new_trip = Trip(id, date, destination_id, milage)
            self.trips.add(new_trip)


@dataclass
class RefuelingTextFileConversion(Conversion):
    '''Class converting data read from file as list of strings to propor objects'''

    refuelings_text_file = TextFile("REFUELINGS.txt")
    refuelings: RefuelingRepository

    def convert(self) -> None:
        refuelings = self.refuelings_text_file.read()
        for line in refuelings:
            data = line.split('\t')
            id = int(data[0])
            date = datetime(data[1])
            volume = float(data[2])
            destination_id = int(data[3])
            new_refueling = Refueling(id, date, volume, destination_id)
            self.refuelings.add(new_refueling)



def main():
    #  Only for testing
    '''destination_1 = Destination(0, "Dest_1", "Location_1", 1000)
    destination_2 = Destination(1, "Dest_2", "Location_2", 2000)
    destination_3 = Destination(2, "Dest_3", "Location_3", 3000)'''
    destinations = DestinationRepository()
    '''destinations.add(destination_1)
    destinations.add(destination_2)
    destinations.add(destination_3)
    for destination in destinations.elements_list:
        print(destination)
    destinations.delete(destination_1)
    print("DELETED")
    for destination in destinations.elements_list:
        print(destination)
    destination_1 = Destination(1, "Dest_2+", "Location_2+", 2001)
    destinations.update(destination_1)
    print("Updated")
    for destination in destinations.elements_list:
        print(destination)
        '''
    text_file = TextFile("DESTINATIONS.txt")
    output = text_file.read()
    # print(output)
    conversion = TextFileConversion(destinations=destinations)
    conversion.destination_conversion()
    for destination in destinations.elements_list:
        print(destination)


if __name__ == "__main__":
    main()
