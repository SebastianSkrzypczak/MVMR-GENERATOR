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

    def __str__(self):
        keys = ''
        for key in self.options.keys():
            keys += key + ', '
        return f'user input = {self.user_input} NOT IN options = {keys}'


class AbstractValidation(ABC):
    '''Generic class to handle validation process'''
    def __init__(self, options) -> None:
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
        if input_data in self.options:
            return self.options[input_data]


def main():
    options = {
        "Y": True,
        "N": False
    }
    input_data = "o"
    validation = TextValidation(options)
    print(validation.check(input_data))


if __name__ == "__main__":
    main()