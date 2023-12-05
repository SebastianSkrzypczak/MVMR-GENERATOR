from abc import ABC, abstractmethod
from domain import model
from typing import TextIO
from icecream import ic


class AbstractRepository(ABC):
    @abstractmethod
    def add(self):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def delete(self):
        pass


class TxtRepository(ABC):
    def __init__(self, file: TextIO, type: model.Item) -> None:
        self.item_type = type
        self.file = file
        self.content: list[model.Item] = None
        self.new_items: list[model.Item] = []
        super().__init__()

    def __create_item_instance(self, item_data: dict) -> model.Item:
        item_instace = self.item_type(**item_data)
        return item_instace

    def __find_item(self, item_id: str) -> model.Item | None:
        content_item = next(
            content_item for content_item in self.content if content_item.id == item_id
        )
        return content_item

    def add(self, item: model.Item):
        self.new_items.append(item)

    def read(self):
        self.content = []
        keys = self.file.readline().strip().split()
        for line in self.file.readlines():
            values = line.strip().split("	")
            data = dict(zip(keys, values))
            item_instance = self.__create_item_instance(data)
            self.content.append(item_instance)

    def update(self, old_item_id: str, new_item: model.Item):
        content_item = self.__find_item(old_item_id)
        if content_item:
            for attr_name in dir(content_item):
                if not callable(
                    getattr(content_item, attr_name)
                ) and not attr_name.startswith("__"):
                    setattr(content_item, attr_name, getattr(new_item, attr_name))
        else:
            raise KeyError

    def delete(self, item_to_delete: None):
        content_item = self.__find_item(item_to_delete)
        if content_item:
            self.content.remove(content_item)
        else:
            raise KeyError
