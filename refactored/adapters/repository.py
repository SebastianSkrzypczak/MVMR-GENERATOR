from abc import ABC, abstractmethod
from domain import model
from typing import TextIO
from datetime import datetime
from icecream import ic
from sqlalchemy import orm

from refactored.domain import model


class AbstractRepository(ABC):
    @abstractmethod
    def __init__(self, type: model.Item) -> None:
        self.item_type = type
        self.content: list[model.Item] = None
        self.new_items: list[model.Item] = []

    @abstractmethod
    def add(self, item: model.Item):
        if not any(True for content_item in self.content if content_item.id == item.id):
            self.new_items.append(item)

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def update(self, old_item_id: str, new_item: model.Item):
        content_item = self._find_item(old_item_id)
        if content_item:
            for attr_name in dir(content_item):
                if not callable(
                    getattr(content_item, attr_name)
                ) and not attr_name.startswith("__"):
                    setattr(content_item, attr_name, getattr(new_item, attr_name))
        else:
            raise KeyError

    @abstractmethod
    def delete(self, item_to_delete: model.Item):
        content_item = self._find_item(item_to_delete)
        if content_item:
            self.content.remove(content_item)
        else:
            raise KeyError


class TxtRepository(AbstractRepository):
    def __init__(self, file: TextIO, type: model.Item) -> None:
        self.item_type = type
        self.file = file
        self.content: list[model.Item] = None
        self.new_items: list[model.Item] = []
        self.header = None

    def _create_item_instance(self, item_data: dict) -> model.Item:
        item_instace = self.item_type(**item_data)
        return item_instace

    def _find_item(self, item_id: str) -> model.Item | None:
        try:
            content_item = next(
                content_item
                for content_item in self.content
                if content_item.id == item_id
            )
        except StopIteration:
            raise StopIteration
        return content_item

    def add(self, item: model.Item):
        super(TxtRepository, self).add(item)

    def read(self):
        self.content = []
        self.header = self.file.readline()
        keys = self.header.strip().split()
        for line in self.file.readlines():
            values = line.strip().split()
            data = dict(zip(keys, values))
            if "date" in keys:
                year, month, day = map(int, data["date"].split("-"))
                data["date"] = datetime(year, month, day).date()
            if "distance" in keys:
                data["distance"] = float(data["distance"])
            item_instance = self._create_item_instance(data)
            self.content.append(item_instance)

    def update(self, old_item_id: str, new_item: model.Item):
        super(TxtRepository, self).update(old_item_id, new_item)

    def delete(self, item_to_delete: model.Item):
        super(TxtRepository, self).delete(item_to_delete)


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, item_type: model.Item, session: orm.session):
        self.type = item_type
        self.session = session
        self.content: list[model.Item] = None
        self.new_items: list[model.Item] = []

    def read(self):
        self.content = self.session.query(self.item_type)

    def add(self, item: model.Item):
        super().add(item)

    def update(self, old_item_id: str, new_item: model.Item):
        super().update(old_item_id, new_item)

    def delete(self, item_to_delete: model.Item):
        return super().delete(item_to_delete)
