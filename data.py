from abc import ABC, abstractmethod


class Crud(ABC):

    @abstractmethod
    def create():
        pass

    @abstractmethod
    def read():
        pass

    @abstractmethod
    def update():
        pass

    @abstractmethod
    def delete():
        pass

class TextFileRepository(Crud):

    def create():
        pass

    def read():
        

