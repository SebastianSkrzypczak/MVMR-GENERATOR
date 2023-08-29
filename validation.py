from abc import ABC, abstractmethod
from datetime import datetime
import errors

'''
Module responsible for all kinds of data validation
'''


class AbstractValidation(ABC):
    '''Generic class to handle validation process'''

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def check(self, input_data):
        pass


class TextValidation(AbstractValidation):
    '''Class to handle text validation process'''

    def check(self, input_data: str, options: dict):
        input_data = input_data.capitalize()
        if input_data in options:
            return options[input_data]
        else:
            raise errors.OptionValidationError(input_data, options)


class NumberValidation(AbstractValidation):
    '''Class to handle numbers validation process'''

    def check(self, input_data):
        pass


class NameValidation(AbstractValidation):
    '''Class to handle new destination values validation process'''

    def check(self, given_name: str, options):
        names_list = [option
                      for option in options
                      if given_name == option.name]
        if names_list:
            raise errors.NameAllredyUsedError(given_name, names_list)


class IdValidation(AbstractValidation):
    '''Class to handle new destination values validation process'''

    def check(self, given_id: str, options):
        id_list = [option for option in options if given_id == str(option.id)]
        if id_list == []:
            raise errors.IdNotFoundError(given_id)


class InRangeValidation(AbstractValidation):
    '''Class to handle validation of user input of distance'''

    def __init__(self, max_value: float, min_value: float) -> None:
        self.max_value = max_value
        self.min_value = min_value

    def check(self, distance: float):
        if not (self.min_value < float(distance) < self.max_value):
            raise errors.NotInRangeError(self.max_value, self.min_value)


class DateValidation(AbstractValidation):
    '''Class to handle date validation'''
    def __init__(self) -> None:
        self.formats = ["%Y.%m.%d", "%Y,%m,%d", "%Y/%m/%d", "%Y-%m-%d"]

    def check(self, date) -> datetime:
        not_correct_format = True
        for format in self.formats:
            try:
                date_obj = datetime.strptime(date, format)
                return date_obj
            except ValueError:
                pass
        if not_correct_format:
            raise errors.DateFormatError
