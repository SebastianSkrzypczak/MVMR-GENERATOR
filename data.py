from abc import ABC, abstractmethod


class Crud(ABC):

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


class Validation():
    def __init__(self,  options) -> None:
        self.options = options

    def check(self, input_data):
        if input_data in self.options:
            return self.options[self.input]


class TextFileRepository(Crud):
    def __init__(self, file_name) -> None:
        self.file_name = file_name
        self.output = []

    def open_file(self, mode="r"):
        try:
            return open(self.name, mode, encoding="utf-8")
        except FileNotFoundError as e:
            raise FileNotFoundError(f'File now found error {e}')
        except IOError as e:
            raise IOError(f"File opening error {e}")

    def create(self, new_data) -> None:
        self.read()
        with self.open_file(mode="a") as file:
            file.write(new_data + '\n')

    def read(self) -> None:
        with self.open_file() as file:
            self.output = file.readlines

    def update(self, old_data, new_data):
        self.read()
        with self.open_file(mode="w") as file:
            pass

    def delete(self):
        self.read()


def main():
    options = {
        "Y": True,
        "N": False
    }
    input_data = "Y"
    validation = Validation(input_data, options)
    print(validation.check())


if __name__ == "__main__":
    main()