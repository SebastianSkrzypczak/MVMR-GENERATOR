from adapters import repository
from abc import ABC, abstractmethod
from domain import model


class AbstractUnitOfWork(ABC):
    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exttype: Exception, exc_value, traceback):
        pass

    @abstractmethod
    def rollback(self, content: list):
        pass

    @abstractmethod
    def commit(self, content: list):
        pass


class TxtUnitOfWork(AbstractUnitOfWork):
    def __init__(self, item_type: model.Item):
        self.item_type = item_type
        self.file_path = rf"refactored\files\{str(item_type.__name__).upper()}S.txt"
        self.backup_content = None
        self.txt_repository = None

    def __enter__(self):
        with open(self.file_path, "r") as file:
            self.txt_repository = repository.TxtRepository(file, self.item_type)
            self.txt_repository.read()
            self.backup_content = self.txt_repository.content

    def commit(self):
        new_content = []
        for item in self.txt_repository.content:
            new_content.append(str(item))
        with open(self.file_path, "w") as file:
            file.write(self.txt_repository.header)
            file.writelines(line + "\n" for line in new_content)

    def rollback(self):
        self.txt_repository.content = self.backup_content
        self.commit()

    def __exit__(self, exttype: Exception, exc_value, traceback):
        if not exttype:
            if self.txt_repository.new_items:
                self.txt_repository.content.append(self.txt_repository.new_items)
            self.commit()
        else:
            self.rollback()
