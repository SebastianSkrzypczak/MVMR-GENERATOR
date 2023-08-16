from abc import ABC, abstractmethod
from dataclasses import dataclass
import data


class Menu(ABC):
    pass


class ValidationError(BaseException):
    '''Custom error to handle validation'''
    def __init__(self, user_input, options: dict) -> None:
        self.user_input = user_input
        self.options = options

    def __str__(self) -> str:
        keys = ''
        for key in self.options.keys():
            keys += key + ', '
        return f'user input = {self.user_input} NOT IN options = {keys}'


class DestinationNameAllredyUsedError(BaseException):
    '''Custom error to handle destination name repetition'''
    def __init__(self, name, destinations) -> None:
        self.name = name
        self.destinations = destinations

    def __str__(self) -> str:
        message = ""
        for destination in self.destinations:
            message += str(destination)
        return f'\n name: {self.name} \n allredy used in \n {message}'


class NotADigitError(BaseException):
    '''Custom error to handle wrong type of input data'''

    def __str__(self) -> str:
        return f'Input must be an integer!'


class NotInRangeError(BaseException):
    '''Custom error to handle range validation error'''
    def __init__(self, max_value, min_value) -> None:
        self.max_value = max_value
        self.min_value = min_value

    def __str__(self) -> str:
        return f'Input must be between {self.min_value} and {self.max_value}!'


class AbstractValidation(ABC):
    '''Generic class to handle validation process'''

    def __init__(self, options=[]) -> None:
        super().__init__()
        self.options: dict = options

    @abstractmethod
    def check(self, input_data):
        pass


class TextValidation(AbstractValidation):
    '''Class to handle text validation process'''

    def check(self, input_data: str):
        input_data = input_data.capitalize()
        if input_data in self.options:
            return self.options[input_data]
        else:
            raise ValidationError(input_data, self.options)


class NumberValidation(AbstractValidation):
    '''Class to handle numbers validation process'''

    def check(self, input_data):
        pass


class DestinationNameValidation(AbstractValidation):
    '''Class to handle new destination values validation process'''

    def check(self, destination_name):
        names_list = [destination
                      for destination in self.options
                      if destination_name == destination.name]
        if names_list:
            raise DestinationNameAllredyUsedError(destination_name, names_list)


class DestinationDistanceValidation(AbstractValidation):
    '''Class to handle validation of user input of distance'''

    def __init__(self, max_distance: float, min_distance: float) -> None:
        self.max_distance = max_distance
        self.min_distance = min_distance

    def check(self, distance: float):
        if not distance.isdigit():
            raise NotADigitError()
        if not (self.min_distance < float(distance) < self.max_distance):
            raise NotInRangeError()
