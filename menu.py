class Validation():
    def __init__(self,  options) -> None:
        self.options = options

    def check(self, input_data):
        if input_data in self.options:
            return self.options[self.input]


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