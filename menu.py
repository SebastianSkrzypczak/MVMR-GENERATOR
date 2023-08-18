from tabulate import tabulate
from datetime import datetime
import data
import validation
import errors

'''
Module responsible for UI.
'''


class UserInput:

    def __init__(self, destinations, refuelings, trips) -> None:
        self.destinations: data.DestinationRepository = destinations
        self.refuelings: data.RefuelingRepository = refuelings
        self.trips: data.TripsRepository = trips

    def options_input(self, options: dict, message: str) -> object:
        options_validation = validation.TextValidation
        while True:
            user_input = input(f'{message}')
            try:
                options_validation.check(user_input)
                options[user_input]
                break
            except errors.OptionValidationError as error:
                print(error)
        return options[user_input]

    def name_input(self, options) -> str:
        name_validation = validation.NameValidation(options=options)
        while True:
            name = input("\nType new name: ")
            try:
                name_validation.check(given_name=name)
                break
            except errors.NameAllredyUsedError as error:
                print(error)
        return name

    def id_input(self, options) -> data.Refueling:
        id_validation = validation.IdValidation(options=options)
        while True:
            id = input("\nType destination ID\n")
            try:
                id_validation.check(id)
                break
            except errors.IdNotFoundError as error:
                print(error)
        return options.elements_list[int(id)-1]

    def distance_input(self) -> float:
        distance_validation = validation.InRangeValidation(
            max_distance=1000,
            min_distance=0)
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
                date_validation.check(date)
                break
            except errors.DateFormatError as error:
                print(error)


class Menu(UserInput):
    '''Abstract class to store generic menu page'''

    def __init__(self, destinations, refuelings, trips) -> None:
        super().__init__(destinations, refuelings, trips)
        self.methods = self.get_methods_as_dict()

    def get_methods_as_dict(self) -> list[str, object]:
        '''Function adding all user methods to dictionary with 
        method's name as key and object adress as value'''

        methods = []

        for method in dir(self.__class__):
            if callable(getattr(self.__class__, method)) and \
               not method.startswith("__") and method.startswith("_"):
                name = method.replace('_', ' ')
                name = name[:3] + name[3].upper() + name[4:]
                pointer = getattr(self.__class__, method)
                user_method = [name, pointer]
                methods.append(user_method)
        return methods

    def index(self) -> None:
        while True:
            print("\nWelcome in MVMR-GENERATOR!\n")
            for method in self.methods:
                print(method[0])
            print('\n')
            choose = int(input('Chose function\n'))-1
            # TODO: validation!!!
            self.methods[choose][1](self)

    def _1_generate_new_MVMR(self):
        pass

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
        print(tabulate(self.refuelings,
                       headers=['ID', 'DATE', 'VOLUME', 'DESTINATION'],
                       tablefmt='grid'
                       ))

    def _5_show_all_destinations(self):
        print(tabulate(self.destinations,
                       headers=['ID', 'NAME', 'LOCATION', 'DISTANCE'],
                       tablefmt='grid'
                       ))


def main():
    menu = Menu(destinations=data.destinations, refuelings=data.refuelings, trips=data.trips)
    menu.index()


if __name__ == "__main__":
    main()
