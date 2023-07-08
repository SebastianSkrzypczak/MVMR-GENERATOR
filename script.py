from collections import namedtuple
from calendar import monthrange
from operator import attrgetter
from tabulate import tabulate
from datetime import datetime
import random


class FileManager:
    def __init__(self, file_name):
        self.file_name = file_name

    def read_with_error_check(self):
        '''
        A function that:
        -> opens file with given name,
        -> checks if errors ocured,
        -> rewrites it to new variable,
        -> closes the original file,
        -> returns output as list of strings:
        (one string is one line from base file)
        '''
        try:
            file = open(self.file_name, "r", encoding="utf8")
        except FileNotFoundError:
            print(f'File {self.file_name} not found')
            return False
        except IOError:
            print(f'Error reading the {self.file_name} file')
            return False
        output = []
        for line in file:
            output.append(line)
        file.close()
        return output

    def write_with_error_check(self, data):
        '''
        A function that:
        -> opens file with given name,
        -> check if errors ocured,
        -> writes given data line by line,
        -> closes the original file.
        '''
        try:
            file = open(self.file_name, "a", encoding="utf8")
        except FileNotFoundError:
            print(f'File {self.file_name} not found')
            return False
        except IOError:
            print(f'Error reading the {self.file_name} file')
            return False
        for line in data:
            file.write(f'{line}/n')
        file.close()
        return


class DestinationManager:
    def __init__(self, file_name):
        self.file_manger = FileManager(file_name)
        self.destinations = self.file_manger.read_with_error_check()

    def read(self):
        '''
        This function gest list of strings and rewrites it
        as list of namedtupes ordered by distance.
        '''
        destination_tuple = namedtuple(
            'destination',
            ['id', 'name', 'location', 'distance']
        )
        destination_list = []
        for line in self.destinations:
            line = line[:-1]  # Deleting "/n"
            separated = line.split("	")
            temp_line = destination_tuple(
                int(separated[0]),
                separated[1],
                separated[2],
                int(separated[3])
                )
            destination_list.append(temp_line)
        return sorted(
            destination_list,
            key=attrgetter("distance"),
            reverse=True
            )

    def write(self):
        '''
        This function takes data about new destiantion
        from user and writes it to a destination list
        '''
        destination_tuple = namedtuple(
            'destination',
            ['id', 'name', 'location', 'distance']
        )
        new_destination_id = self.destinations[-1].id
        print(f'new_destination_id = {new_destination_id}')
        new_destination_name = input("Type new destination's name: ")
        new_destination_location = input("Type new destination's location: ")
        while True:
            new_destination_distance = input(
                "Type new destination's distance: "
                )
            if (new_destination_distance.isdigit()
                    and int(new_destination_distance) > 0
                    and int(new_destination_distance) < 10000):
                break
            else:
                print("Distance must be an integer between 0 and 10000")
        new_destination = destination_tuple(
            int(new_destination_id),
            new_destination_name,
            new_destination_location,
            int(new_destination_distance)
            )
        destination_list = self.destinations
        destination_list.append(new_destination)
        self.destinations = sorted(
            destination_list,
            key=attrgetter("distance"),
            reverse=True
            )
        return


class RefuelingsManager:
    def __init__(self, file_name, destinations):
        self.file_manger = FileManager(file_name)
        self.refuelings = self.file_manger.read_with_error_check()
        self.destinations = destinations

    def read(self):
        '''
        This function gest list of strings and rewrites
        it as a list of namedtupes
        sorted by dates of refueling.
        '''
        fuel_tuple = namedtuple(
            'refueling',
            ['date', 'volume', 'name']
        )
        fuel_list = []
        for line in self.refuelings:
            line = line[:-1]  # deleting "/n"
            separated = line.split("	")
            temp_line = fuel_tuple(
                separated[0],
                int(separated[1]),
                separated[2])
            fuel_list.append(temp_line)
        return sorted(fuel_list, key=attrgetter('date'))

    def write(self):
        '''
        This function takes data about new refueling
        from user and writes it to a refuelings list
        '''
        destination_tuple = namedtuple(
            'refueling',
            ['date', 'volume', 'name']
        )
        while True:
            date = input(
                "Type new refueling's date in format YYYY.MM.DD: "
                )
            try:
                datetime.strptime(date, "%Y.%m.%d")
                break
            except ValueError:
                print("Incorrect format of date")
        while True:
            volume = input(
                "Type new refueling's volume: "
                )
            if (volume.isdigit()
                    and int(volume) > 0
                    and int(volume) < 200):
                break
            else:
                print("Volume must be an integer between 0 and 200")
        for index, destination in enumerate(self.destinations):
            print(f'{destination.id}:     {destination.name}')
        while True:
            id = input(
                "Type new refueling's nearest location ID from list above: "
                )
            if id > 0 and id < len(destination):
                break
            else:
                print('ID must be and integer')
        new_destination = destination_tuple(
            date,
            int(volume),
            int(id)
            )
        destination_list = self.refuelings
        destination_list.append(new_destination)
        self.refuelings = sorted(
            destination_list,
            key=attrgetter("distance"),
            reverse=True
            )
        return


def recalculate(trips_list, prev_milage):
    '''
    Function takes two arguments:
    -> trips_list - genereted in trips() list of all trips in given month,
    -> prev_milage - milage from previous month
    and:
    -> adds distance by every trip,
    -> rewrites it to required format.
    '''
    trips_tuple = namedtuple(
        'trip',
        ['date', 'name', 'distance', 'location', 'milage_now']
    )
    last = prev_milage
    trip_recalc = []
    for trip in trips_list:
        date = trip.date
        name = trip.name
        distance = trip.distance
        location = trip.location
        milage_now = str(last + int(distance))
        last = last + int(distance)
        temp = trips_tuple(date, name, distance, location, milage_now)
        trip_recalc.append(temp)
    return trip_recalc


def trips(
        dest_list, fuel_list,
        prev_milage, current_milage,
        month, year, free_days
        ):
    '''
    In this function a milage records table is beeing generated.
    The function takes following arguments:
    -> dest_list - a list od destinations read in dest(),
    -> fuel_list - a list of refuelings read in fuel(),
    -> prev_milage - milage from last month,
    -> current_milage,
    -> month,
    -> year.
    '''
    trips_tuple = namedtuple(
        'trip',
        ['date', 'name', 'distance', 'location', 'milage_now']
    )
    month_range = current_milage - prev_milage
    days = monthrange(year, month)[1]
    if month < 10:
        month = "0" + str(month)
    else:
        month = str(month)
    iteration = 0
    while True:
        used_range = 0
        trips_list = []
        for fuel_tuple in fuel_list:
            fuel_name = fuel_tuple.name
            try:
                temp_destination = (
                    dest
                    for dest in dest_list
                    if dest.name == fuel_name
                    )
                next_destination = next(temp_destination)
                temp_name = next_destination.name
                temp_distance = next_destination.distance
                temp_location = next_destination.location
                temp = trips_tuple(
                    fuel_tuple.date,
                    temp_name,
                    temp_distance,
                    temp_location,
                    "0"
                )
                trips_list.append(temp)
            except StopIteration:
                continue
        day_iteration = 0  # Safety variable to avoid too long looping
        while used_range < month_range:
            if day_iteration < 30:
                random_day = random.randrange(1, days)
                if random_day < 10:
                    random_date = ('0'
                                   + str(random_day)
                                   + '.'
                                   + str(month)
                                   + '.'
                                   + str(year)
                                   )
                else:
                    random_date = (
                        str(random_day)
                        + '.'
                        + str(month)
                        + '.'
                        + str(year))
                if (not any([
                    True
                    for trip in trips_list
                    if trip.date == random_date
                    ]) and  # checking if generated day is allredy used
                    not any([
                        True
                        for days in free_days
                        if days == random_date
                        ])):  # checking if generated day is a free day
                    trip_iteration = 0  # safety variable to avoid too long looping
                    while True:
                        if trip_iteration < 30:
                            if month_range - used_range > 70:  # factor determining which trips should be taken first
                                factor_1 = 1
                                factor_2 = 15
                            else:
                                factor_1 = 15
                                factor_2 = len(dest_list)-1
                            random_destination = dest_list[random.randrange(factor_1, factor_2)]  # picking random destionation from dest_list
                            if used_range + int(random_destination.distance) < month_range:
                                ran_day_trip = trips_tuple(
                                    random_date,
                                    random_destination.name,
                                    str(random_destination.distance),
                                    random_destination.location,
                                    "0")
                                trips_list.append(ran_day_trip)
                                used_range = used_range + int(random_destination.distance)
                                trip_iteration += 1
                                break
                            else:
                                break
                        else:
                            break
                day_iteration += 1
            else:
                break
        if month_range - used_range <= 30:  # if difference is greater than ... script should start again.
            break
        else:
            iteration += 1
    trips_sorted = sorted(trips_list, key=attrgetter('date'))
    return recalculate(trips_sorted, prev_milage), used_range, iteration


class Menu:
    def __init__(self, destination_manager, refuelings_manger):
        self.destination_manager = destination_manager
        self.refuelings_manger = refuelings_manger

    def get_milage(prev_milage, message):
        '''
        A function that takes input with milage from user and check,
        if it meets the assumptions.
        '''
        while True:
            try:
                milage = int(input(f'Type milage from {message} month: '))
                if milage <= 0:
                    raise ValueError("Input must be a positive integer")
                if milage <= prev_milage:
                    raise ValueError(
                        "Input must be larger that previous milage"
                        )
                return milage
            except TypeError as error:
                print(f'Type error: {error}')
            except ValueError as error:
                print(f'Value error: {error}')

    def add_destination(self):
        self.destination_manager.write()

    def add_refueling(self):
        self.refuelings_manger.write()

    def date_input(self):
        month = 0


def main():
    destinations_manager = DestinationManager("DESTINATIONS.txt")
    destinations = destinations_manager.read()
    refuelings_manager = RefuelingsManager("REFUELINGS.txt", destinations)
    menu = Menu(destinations_manager, refuelings_manager)
    refuelings_manager.write()
    refuelings = refuelings_manager.read()
    prev_milage = menu.get_milage(0, 'previous')
    current_milage = menu.get_milage(prev_milage, 'current')
    month = 4
    year = 2023
    trips_, range_, iteration_ = trips(
        destinations,
        refuelings,
        prev_milage,
        current_milage,
        month, year,
        free_days=[]
        )
    print(tabulate(
        trips_,
        headers=["DATE", "NAME", "DISTANCE", "LOCATION", "MILAGE"],
        tablefmt="grid"
        ))
    print(f'range {range_}')
    print(f'iteration {iteration_}')


if __name__ == "__main__":
    main()
