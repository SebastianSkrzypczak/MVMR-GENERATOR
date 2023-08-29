from tabulate import tabulate
from datetime import datetime
import data
import validation
import errors
import script_

'''
Module responsible for UI in command prompt.
'''


class UserInput:

    '''A class handling user input validation and running process'''

    def __init__(self, destinations, refuelings, trips) -> None:
        self.destinations: data.DestinationRepository = destinations
        self.refuelings: data.RefuelingRepository = refuelings
        self.trips: data.TripsRepository = trips

    def options_input(self, options: list, message: str) -> object:

        '''A function responsible for running
          options from menu after input validation'''

        options_validation = validation.TextValidation()
        while True:
            user_input = input(f'{message}')
            try:
                options_validation.check(input_data=user_input, options=options)
                options[user_input.upper()]
                break
            except errors.OptionValidationError as error:
                print(error)
        return options[user_input.upper()]

    def name_input(self, options) -> str:
        name_validation = validation.NameValidation()
        while True:
            name = input("\nType new name: ")
            try:
                name_validation.check(given_name=name, options=options)
                break
            except errors.NameAllredyUsedError as error:
                print(error)
        return name

    def id_input(self, options) -> data.Refueling:
        id_validation = validation.IdValidation()
        while True:
            id = input("\nType destination ID\n")
            try:
                id_validation.check(id, options=options)
                break
            except errors.IdNotFoundError as error:
                print(error)
        return options.elements_list[int(id)-1]

    def distance_input(self) -> float:
        distance_validation = validation.InRangeValidation(
            max_value=1000,
            min_value=0
        )
        while True:
            new_destination_distance = (input(
                "Type new destination's distance: "
                ))
            try:
                distance_validation.check(new_destination_distance)
                break
            except errors.NotADigitError as error:
                print(error)
            except errors.NotInRangeError as error:
                print(error)
        return float(new_destination_distance)

    def volume_input(self) -> float:
        volume_validation = validation.InRangeValidation(
            max_value=200,
            min_value=0)
        while True:
            new_refueling_volume = (input(
                "Type new refueling's volume: "
                ))
            try:
                volume_validation.check(new_refueling_volume)
                break
            except errors.NotADigitError as error:
                print(error)
            except errors.NotInRangeError as error:
                print(error)
        return float(new_refueling_volume)

    def location_input(self) -> str:
        location = input("\nType new destination's location: ")
        return location

    def date_input(self, message) -> datetime:
        while True:
            date_validation = validation.DateValidation()
            date = input(message)
            try:
                date = date_validation.check(date)
                return date
            except errors.DateFormatError as error:
                print(error)

    def milage_input(self, message: str, min_value=0.0, max_value=float('inf')) -> int:
        milage_validation = validation.InRangeValidation(max_value, min_value)
        while True:
            user_input = int(input(message))
            try:
                milage_validation.check(user_input)
                return user_input
            except errors.NotInRangeError as error:
                print(error)


class Menu(UserInput):
    '''Abstract class to store generic menu page'''

    def __init__(self, destinations, refuelings, trips) -> None:
        super().__init__(destinations, refuelings, trips)
        self.methods: dict = self.get_methods_as_list()

    def get_methods_as_list(self) -> list[set]:
        '''Function adding all user methods to dictionary with
        method's name as key and object adress as value'''

        methods = []

        for method in dir(self.__class__):
            if callable(getattr(self.__class__, method)) and \
               not method.startswith("__") and method.startswith("_"):
                name = method.replace('_', ' ')
                name = name[:3] + name[3].upper() + name[4:]
                pointer = getattr(self.__class__, method)
                method_set = (name, pointer)
                methods.append(method_set)
        return methods

    def index(self) -> None:
        while True:
            print("\nWelcome in MVMR-GENERATOR!\n")
            for method in self.methods:
                print(f'{method[0]}\n')
            # self.options_input(self.methods, 'Chose function\n')
            choose = int(input('Chose function\n'))-1
            # self.options_input(self.methods, '')
            self.methods[choose][1](self)

    def _1_generate_new_MVMR(self):
        settings = {
                    'day_iteration': 10,
                    'trip_iteration': 30,
                    'factor': 15,
                    'max_difference': 50
                    }
        date = self.date_input('Type start-date of MVMR (YYYY/MM/DD)\n')
        if len(self.trips.elements_list) > 0:
            previous_milage = self.trips.elements_list[-1].milage
        else:
            previous_milage = self.milage_input('Type last previous month milage\n')
        current_milage = self.milage_input(
                                          'Type current milage\n',
                                          min_value=previous_milage
                                          )
        generator = script_.Generator(
                                    self.destinations,
                                    self.refuelings,
                                    self.trips,
                                    previous_milage,
                                    current_milage,
                                    date,
                                    settings
                                    )
        generator.generate()
        table = tabulate(generator.trips_list,
                       headers=['DATE', 'DESTINATION', 'MILAGE'],
                       tablefmt='grid'
                       )
        print(table)
        save = self.options_input({'Y': True, 'N': False}, "Do You want to save MVMR?\n")
        if save:
            trips_file = data.TextFile("TRIPS.txt")
            for trip in generator.trips_list:
                self.trips.add(trip)
                line = f'{trip.id}\t{trip.date}\t{trip.destination}\t{trip.milage}'
                trips_file.create(line)


    def _2_add_new_destination(self) -> None:
        while True:
            if len(self.destinations.elements_list) > 0:
                new_destination_id = int(self.destinations.elements_list[-1].id+1)
            else:
                new_destination_id = 1
            print(f'New destiantions ID: {new_destination_id}')
            new_destination_name = self.name_input(self.destinations)
            new_destination_distance = self.distance_input()
            new_destination_location = self.location_input()
            new_destination = data.Destination(
                id=new_destination_id,
                name=new_destination_name,
                location=new_destination_location,
                distance=new_destination_distance
            )
            table = tabulate([['ID', 'Name', 'Location', 'Distance'],
                              [new_destination_id,
                              new_destination_name,
                              new_destination_location,
                              new_destination_distance]],
                             tablefmt='grid')
            message = f'New destination:\n{table}\nDo You accept? (Y/N)'
            options = {'Y': True,
                       'N': False
                       }
            if self.options_input(options, message):
                break
        self.destinations.add(new_destination)

    def _3_add_new_refueling(self) -> None:
        if len(self.refuelings.elements_list) > 0:
            new_refueling_id = self.refuelings.elements_list[-1].id
        else:
            new_refueling_id = 1
        print(f'New refueling ID: {new_refueling_id}\n')
        new_refueling_date = self.date_input(message='Type new refueling date\n')
        new_refeling_volume = self.volume_input()
        self._5_show_all_destinations()
        new_refeling_destination = self.id_input(self.destinations)
        new_refueling = data.Refueling(
            id=new_refueling_id,
            date=new_refueling_date,
            volume=new_refeling_volume,
            destination=new_refeling_destination
        )
        self.refuelings.add(new_refueling)

    def _4_show_all_refuelings(self):
        all = [
               [refueling.id,
                refueling.date,
                refueling.volume,
                refueling.destination.name]
               for refueling in self.refuelings
               ]
        print(tabulate(all,
                       headers=['ID', 'DATE', 'VOLUME', 'DESTINATION'],
                       tablefmt='grid'
                       ))

    def _5_show_all_destinations(self):
        print(tabulate(self.destinations,
                       headers=['ID', 'NAME', 'LOCATION', 'DISTANCE'],
                       tablefmt='grid'
                       ))

    def _6_show_all_trips(self):
        print(tabulate(self.trips,
                       headers=['DATE', 'DESTINATION', 'MILAGE'],
                       tablefmt='grid'
                       ))


def main():
    menu = Menu(destinations=data.destinations, refuelings=data.refuelings, trips=data.trips)
    menu.index()


if __name__ == "__main__":
    main()
