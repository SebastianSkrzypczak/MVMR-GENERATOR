from abc import ABC, abstractmethod
from dataclasses import dataclass
import data
import validation


class UserInput:

    def __init__(self, destinations, refuelings, trips) -> None:
        self.destinations: data.DestinationRepository = destinations
        self.refuelings: data.RefuelingRepository = refuelings
        self.trips: data.TripsRepository = trips

    def name_input(self):
        name_validation = validation.DestinationNameValidation(options=self.destinations)
        while True:
            name = input("\nType new destination's name: ")
            try:
                name_validation.check(destination_name=name)
                break
            except validation.DestinationNameAllredyUsedError as error:
                print(error)
        return name

    def distance_input(self):
        distance_validation = validation.DestinationDistanceValidation(
            max_distance=1000,
            min_distance=0)
        while True:
            new_destination_distance = (input(
                "Type new destination's distance: "
                ))
            try:
                distance_validation.check(new_destination_distance)
                break
            except validation.NotADigitError as error:
                print(error)
            except validation.NotInRangeError as error:
                print(error)
        return float(new_destination_distance)


class Menu(UserInput):
    '''Abstract class to store generic menu page'''

    def get_methods_as_dict(self) -> list:
        '''Function adding all user methods to dictionary with 
        method's name as key and object adress as value'''

        methods = []

        for method in dir(self.__class__):
            if callable(getattr(self.__class__, method)) and \
               not method.startswith("__") and method.startswith("_"
                                                                 ):
                name = method.replace('_', ' ')
                name = name[:3] + name[3].upper() + name[4:]
                pointer = getattr(self.__class__, method)
                user_method = [name, pointer]
                methods.append(user_method)
        return methods

    def index(self):
        print("\nWelcome in MVMR-GENERATOR!")

    def _1_generate_new_MVMR(self):
        pass

    def _2_add_new_destination(self) -> None:
        new_destination_id = self.destinations.elements_list[-1].id
        print(f'New destiantions ID: {new_destination_id}')
        new_destination_name = self.name_input()
        new_destination_distance = self.distance_input()
        new_destination_location = input("\nType new destination's location: ")
        new_destination = data.Destination(
            id=new_destination_id,
            nam=new_destination_name,
            location=new_destination_location,
            distance=new_destination_distance
        )


    def _3_add_new_refueling(self):
        pass

    def _4_show_all_refuelings(self):
        pass

    def _5_show_all_destinations(self):
        pass


def main():
    data
    menu = Menu(destinations=data.destinations, refuelings=data.refuelings, trips=data.trips)
    #methods = menu.get_methods_as_dict()
    """for method in methods:
        print(method[0])
    new_method = methods[2][1]
    new_method(menu)"""
    menu._2_add_new_destination()

if __name__ == "__main__":
    main()