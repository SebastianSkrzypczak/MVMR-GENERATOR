from tabulate import tabulate
'''
Module storing all custom errros
'''


class OptionValidationError(BaseException):
    '''Custom error to handle validation'''
    def __init__(self, user_input, options: dict) -> None:
        self.user_input = user_input
        self.options = options

    def __str__(self) -> str:
        keys = ''
        for key in self.options.keys():
            keys += key + ', '
        return f'user input = {self.user_input} NOT IN options = {keys}'


class NameAllredyUsedError(BaseException):
    '''Custom error to handle name repetition'''

    def __init__(self, name, destinations) -> None:
        self.name = name
        self.destinations = destinations

    def __str__(self) -> str:
        message = []
        for destination in self.destinations:
            message.append(destination)
        table = tabulate(message,
                         headers=['ID', 'NAME', 'LOCATION', 'DISTANCE'],
                         tablefmt='grid'
                         )
        return f'\n ERROR! Name: {self.name} allredy used in \n {table}'


class IdNotFoundError(BaseException):
    '''Custom error to handle name not existing'''

    def __init__(self, name) -> None:
        self.name = name

    def __str__(self) -> str:
        return f'Name {self.name} not found!'


class NotADigitError(BaseException):
    '''Custom error to handle wrong type of input data'''

    def __str__(self) -> str:
        return 'Input must be an integer!'


class DateFormatError(BaseException):
    '''Custom error to handle wrong format od date'''

    def __str__(self) -> str:
        return '\nIncorrect date format\n'


class NotInRangeError(BaseException):
    '''Custom error to handle range validation error'''
    def __init__(self, max_value, min_value) -> None:
        self.max_value = max_value
        self.min_value = min_value

    def __str__(self) -> str:
        return f'Input must be between {self.min_value} and {self.max_value}!'
    

class TimelineError(BaseException):
    '''Custom error to handle date timeline validation'''
    def __init__(self, last_date) -> None:
        self.last_date = last_date

    def __str__(self) -> str:
        return f'Date must be newer than last recorded trip date: {self.last_date}'
