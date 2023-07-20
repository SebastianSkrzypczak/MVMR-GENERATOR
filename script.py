from collections import namedtuple
from calendar import monthrange
from operator import attrgetter
from tabulate import tabulate
from datetime import datetime
from dateutil.relativedelta import relativedelta
import random


class FileManager:
    def __init__(self, file_name):
        self.file_name = file_name

    def read_with_error_check(self):
        '''
        A function:
        -> opens file with given name,
        -> checks if errors ocured,
        -> rewrites it to new variable,
        -> closes the original file,
        -> returns output as list of strings:
        (one string is one line from base file)
        '''
        try:
            file = open(self.file_name, "r", encoding="utf-8")
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
        A function:
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
            file.write(f'{line}\n')
        file.close()
        return


class DestinationManager:
    def __init__(self, file_name):
        self.file_manger = FileManager(file_name)
        self.destinations = self.file_manger.read_with_error_check()

    def read(self):
        '''
        Function rewriting list of strings, as list of namedtuples.
        IN:
        ->list of strings read from file
        OUT:
        ->sorted list of namedtuples
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
        Function adding new destination to destination list and to file. 
        IN:
        ->User input
        OUT:
        ->New destination writen to file
        '''
        destination_tuple = namedtuple(
            'destination',
            ['id', 'name', 'location', 'distance']
        )
        destinations = self.read()
        # new ID is the last destination on destinations list + 1
        new_destination_id = int(destinations[-1].id)+1 
        print(f'New destiantions ID: {new_destination_id}')
        new_destination_name = input("\nType new destination's name: ")
        new_destination_location = input("\nType new destination's location: ")
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
        table = [
            ["ID", new_destination_id],
            ["NAME", new_destination_name],
            ["LOCATION", new_destination_location],
            ["DISTANCE", new_destination_distance]
        ]
        print(tabulate(table, tablefmt="grid"))
        while True:
            user_input = input(
                "\nAll informations correct? If so destination will be saved (Y/N)\n"
                )
            if user_input.capitalize() == "Y":
                destinations.append(new_destination)
                self.destinations = sorted(
                    destinations,
                    key=attrgetter("distance"),
                    reverse=True
                    )
                destination_frmtd = f'{new_destination_id}\t' \
                                    f'{new_destination_name}\t' \
                                    f'{new_destination_location}\t'\
                                    f'{new_destination_distance}'
                data_to_be_saved = []
                data_to_be_saved.append(destination_frmtd)
                try:
                    self.file_manger.write_with_error_check(data_to_be_saved)
                    print("Refueling saved correctly")
                except False:
                    print("An error occurred")
                break
            elif user_input.capitalize() == "N":
                print('\nOK, then start again.\n')
                pass
            else:
                print("\nType Y or N\n")
        return


class RefuelingsManager:
    def __init__(self, file_name, destinations):
        self.file_manger = FileManager(file_name)
        self.refuelings_raw = self.file_manger.read_with_error_check()
        self.refuelings = self.read()
        self.destinations = destinations

    def read(self):
        '''
        Function rewriting list of strings, as list of namedtuples.
        IN:
        ->list of strings read from file
        OUT:
        ->sorted list of namedtuples
        '''
        fuel_tuple = namedtuple(
            'refueling',
            ['date', 'volume', 'name']
        )
        fuel_list = []
        for line in self.refuelings_raw:
            line = line[:-1]  # deleting "/n"
            separated = line.split("\t")
            separated[1] = separated[1].replace(",", ".")
            temp_line = fuel_tuple(
                datetime.strptime(separated[0], "%Y/%m/%d"),
                float(separated[1]),
                separated[2])
            fuel_list.append(temp_line)
        return sorted(fuel_list, key=attrgetter('date'))

    def write(self):
        '''
        Function adding new refueling to refuelings list and to file. 
        IN:
        ->User input
        OUT:
        ->New refueling writen to file
        '''
        formats = ["%Y.%m.%d", "%Y,%m,%d", "%Y/%m/%d", "%Y-%m-%d"]
        # none variable is used to check if data fit any of above formats
        none = False
        refueling_tuple = namedtuple(
            'refueling',
            ['date', 'volume', 'name']
        )
        while True:
            while True:
                date = input(
                    "Type new refueling's date in format YYYY.MM.DD: "
                    )
                for format in formats:
                    try:
                        datetime.strptime(date, format)
                        none = True
                        break
                    except ValueError:
                        pass
                if not none:
                    print("Incorrect format of date")
                else:
                    break
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
            for destination in self.destinations:
                print(f'{destination.id}:     {destination.name}')
            while True:
                id = input(
                    "Type new refueling's nearest location ID from list above: "
                    )
                if int(id) > 0 and  \
                   int(id) <= len(self.destinations):
                    break
                else:
                    print('ID must be and integer')
            new_refueling = refueling_tuple(
                datetime.strptime(date, "%Y/%m/%d"),
                float(volume),
                self.destinations[int(id)-1].name
                )
            print('\nYour new refueling: \n')
            table = [
                ["DATE", new_refueling.date.strftime("%Y-%m-%d")],
                ["VOLUME", new_refueling.volume],
                ["NAME", new_refueling.name]
            ]
            print(tabulate(table, tablefmt="grid"))
            while True:
                user_input = input(
                    "\nAll informations correct? If so refueling will be saved (Y/N)\n"
                    )
                if user_input.capitalize() == "Y" \
                   or user_input.capitalize() == "N":
                    break
                else:
                    print("\nType Y or N\n")
            if user_input.capitalize() == "Y":
                self.refuelings.append(new_refueling)
                self.refuelings = sorted(
                    self.refuelings,
                    key=attrgetter("date"),
                    reverse=False
                )
                format = "%Y/%m/%d"
                refueling_frmtd = f'{new_refueling.date.strftime(format)}\t' \
                                  f'{new_refueling.volume}\t' \
                                  f'{new_refueling.name}'
                data_to_be_saved = []
                data_to_be_saved.append(refueling_frmtd)
                try:
                    self.file_manger.write_with_error_check(data_to_be_saved)
                    print("Refueling saved correctly")
                except False:
                    print("An error occurred")
                break
            elif user_input.capitalize() == "N":
                print('\nOK, then start again.\n')
                pass
            else:
                pass
        return


def recalculate(trips_list, prev_milage):
    '''
    Function adds distance by every trip and rewrites it to required format.
    IN:
    -> trips_list - genereted in trips() list of all trips in given month,
    -> prev_milage - milage from previous month
    OUT:
    ->list of namedtuples in correct format    
    '''
    trips_tuple = namedtuple(
        'trip',
        ['date', 'name', 'distance', 'location', 'milage_now']
    )
    last = prev_milage
    trip_recalc = []
    first_row = [trips_tuple(
        "-",
        "-",
        "-",
        "-",
        prev_milage,
    )]
    trip_recalc = first_row + trip_recalc
    for trip in trips_list:
        date = datetime.strftime(trip.date, "%d-%m-%Y")
        name = trip.name
        distance = trip.distance
        location = trip.location
        milage_now = str(last + int(distance))
        last += int(distance)
        temp = trips_tuple(date, name, distance, location, milage_now)
        trip_recalc.append(temp)
    return trip_recalc


def trips(
        dest_list, fuel_list,
        prev_milage, current_milage,
        month, year, free_days,
        **kwargs
        ):
    '''
    In this function a milage records table is beeing generated.
    IN:
    -> dest_list - a list od destinations read in dest(),
    -> fuel_list - a list of refuelings read in fuel(),
    -> prev_milage - milage from last month,
    -> current_milage,
    -> month,
    -> year.
    OUT:
    ->recalculated() list of trips
    ->used range
    ->iteration of main loop which gave good results
    '''
    set_day_iteration = kwargs.get('set_day_iteration')
    set_trip_iteration = kwargs.get('set_trip_iteration')
    set_factor = kwargs.get('set_factor')
    set_max_difference = kwargs.get('set_max_difference')
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

        # rewriting trips from refuelings list
        for fuel_tuple in fuel_list:
            fuel_month = fuel_tuple.date.month
            if fuel_month == int(month):
                fuel_name = fuel_tuple.name
                temp_destination = (
                    dest
                    for dest in dest_list
                    if dest.name == fuel_name
                    )
                try:
                    next_destination = next(temp_destination)
                except StopIteration:
                    # handling exception if none of destinations 
                    # match refueling destination
                    print("Error has occured. Check data.")
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
                used_range += int(temp_distance)
                trips_list.append(temp)

        day_iteration = 0  # Safety variable to avoid too long looping
        while used_range < month_range:
            # picking random day
            if day_iteration < set_day_iteration:
                random_day = random.randrange(1, days)
                random_date = (
                    str(random_day)
                    + '.'
                    + str(month)
                    + '.'
                    + str(year))
                datetime_random_date = datetime.strptime(
                    random_date,
                    "%d.%m.%Y"
                    )

                if (not any([  # checking if generated day is allready used
                    True
                    for trip in trips_list
                    if trip.date == random_date
                    ]) and
                    not any([  # checking if generated day is a free day
                        True
                        for days in free_days
                        if days == random_date
                        ])):

                    trip_iteration = 0  # safety variable to avoid too long looping
                    while True:
                        # picking destination for random day
                        if trip_iteration < set_trip_iteration:
                            # factor determining which trips should be taken first
                            # (at first it takes the longest trips, and then closest)
                            if month_range - used_range > 70:
                                factor_1 = 1
                                factor_2 = set_factor
                            else:
                                factor_1 = set_factor
                                factor_2 = len(dest_list)-1
                            random_destination = dest_list[
                                random.randrange(factor_1, factor_2)
                                ]  # picking random destionation from dest_list
                            if used_range + int(random_destination.distance) < month_range:
                                ran_day_trip = trips_tuple(
                                    datetime_random_date,
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
        if month_range - used_range <= set_max_difference:  # if difference is greater than set_max_difference script should start again.
            break
        else:
            iteration += 1
    trips_sorted = sorted(trips_list, key=attrgetter('date'))
    return recalculate(trips_sorted, prev_milage), used_range, iteration


class Menu:
    def __init__(self, destination_manager, refuelings_manager, destinations):
        self.destination_manager = destination_manager
        self.refuelings_manager = refuelings_manager
        self.destinations = destinations
        self.file_manager_all = FileManager("TRIPS.txt")

    def show_destinations(self):
        '''
        Function printing all destinations as grid table
        '''
        table = tabulate(
            self.destinations,
            headers=["ID", "NAME", "LOCATION", "DISTANCE"],
            tablefmt="grid"
            )
        print(table)

    def show_refuelings(self):
        '''
        Function printing all refuelings as grid table
        '''
        table = tabulate(
            self.refuelings_manager.read(),
            headers=["DATE", "VOLUME", "NAME"],
            tablefmt="grid"
            )
        print(table)

    def validation(self, user_input, max_value):
        '''
        checking if user input is correct
        '''
        for value in range(0, max_value+1):
            if user_input.isdigit() and int(user_input) == value:
                return value
        raise ValueError

    def generate(self):
        '''
        Function:
        -> collects data from other functions
        ->runs trips()
        ->prints it as grid table
        '''
        month, year = self.date_input()
        self.add_refueling()
        refuelings = self.refuelings_manager.read()
        prev_milage = self.get_milage(0, 'previous')
        current_milage = self.get_milage(prev_milage, 'current')
        trips_, range_, iteration_ = trips(
            self.destinations,
            refuelings,
            prev_milage,
            current_milage,
            month,
            year,
            free_days=[],
            set_day_iteration=15,
            set_trip_iteration=30,
            set_factor=15,
            set_max_difference=30
            )
        month_table = tabulate(
            trips_,
            headers=["DATE", "NAME", "DISTANCE", "LOCATION", "MILAGE"],
            tablefmt="grid"
            )
        all_table = month_table.split("\n")
        month_table = all_table
        all_table = all_table[5:]
        for line in month_table:
            print(line)
        print(f'Used range: {range_}')
        print(f'Result in {iteration_}. iteration')
        # self.file_manager_all.write_with_error_check(all_table)
        # file_manager_month = FileManager(f'{month}_{year}.txt')
        # file_manager_month.write_with_error_check(month_table)

    def index(self):
        print("\nWelcome in MVMR-GENERATOR!")
        table = [
            ["1", "Generate new MVMR"],
            ["2", "Add new destination"],
            ["3", "Add new refueling"],
            ["4", "Show all refuelings"],
            ["5", "Show all destiantions"],
            ["0", "EXIT"]
        ]
        print(tabulate(table, tablefmt="grid"))
        while True:
            user_input = input("\nWhat do You want to do?\n")
            try:
                output = self.validation(user_input, len(table))
                break
            except ValueError:
                print(f"Input must be integer between 0 and {len(table)}")
        if output == 1:
            self.generate()
        elif output == 2:
            self.add_destination()
        elif output == 3:
            self.add_refueling()
        elif output == 4:
            self.show_refuelings()
        elif output == 5:
            self.show_destinations()
        elif output == 0:
            exit(0)

    def get_milage(self, prev_milage, message):
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
        run_manager = False
        while True:
            if run_manager:
                self.destination_manager.write()
                run_manager = False
            next = input("\nDo You want to add another destination? (Y/N)\n")
            if next.capitalize() == "N":
                break
            elif next.capitalize() == "Y":
                run_manager = True
            else:
                print("Type Y or N")

    def add_refueling(self):
        run_manager = False
        while True:
            if run_manager:
                self.refuelings_manager.write()
                run_manager = False
            next = input("\nDo You want to add another refueling? (Y/N)\n")
            if next.capitalize() == "N":
                break
            elif next.capitalize() == "Y":
                run_manager = True
            else:
                print("Type Y or N")

    def date_input(self):
        today = datetime.today().replace(day=1)
        current_month = today.strftime("%B")
        previous_month = (today - relativedelta(days=1)).strftime("%B")
        year = today.year
        table = [
            ["1.", f'{current_month} {year}'],
            ["2.", f'{previous_month} {year}'],
            ["3.", "Different month"],
        ]
        print(tabulate(table, tablefmt='grid'))
        while True:
            chose = input("\nWhich month do You choose? (1/2/3)\n")
            if chose.isdigit() and int(chose) == 1:
                month = today.month
                break
            elif (chose.isdigit() and int(chose) == 2):
                month = today.month - 1
                break
            elif (chose.isdigit() and int(chose) == 3):
                formats = ["%Y.%m", "%Y,%m", "%Y/%m", "%Y-%m"]
                while True:
                    other_date = input("\nType date in format YYYY-MM\n")
                    for format in formats:
                        try:
                            month = datetime.strptime(other_date, format).month
                            break
                        except ValueError:
                            month = None
                    if month is None:
                        print("\nType date in correct format\n")
                    else:
                        break
                break
            else:
                print("Chose must be an integer between 1 and 3")
        return month, year


def main():
    while True:
        destinations_manager = None
        destinations_manager = DestinationManager("DESTINATIONS.txt")
        destinations = destinations_manager.read()
        refuelings_manager = None
        refuelings_manager = RefuelingsManager("REFUELINGS.txt", destinations)
        menu = Menu(destinations_manager, refuelings_manager, destinations)
        menu.index()


if __name__ == "__main__":
    main()
