from abc import ABC, abstractmethod
from domain import model
from typing import TextIO
from datetime import datetime
from icecream import ic
from sqlalchemy import orm


class AbstractRepository(ABC):
    @abstractmethod
    def __init__(self, type: model.Item) -> None:
        self.item_type = type
        self.content: list[model.Item] = None

    def find_item(self, item_id: str) -> model.Item | None:
        try:
            content_item = next(
                content_item
                for content_item in self.content
                if content_item.id == item_id
            )
        except StopIteration:
            raise StopIteration
        return content_item

    def _check_if_item_in_content(self, item: model.Item) -> bool:
        return any(True for content_item in self.content if content_item.id == item.id)

    @abstractmethod
    def add(self, item: model.Item) -> None:
        ic(self._check_if_item_in_content(item))
        if self.content is None:
            self.content = []
            self.content.append(item)
            ic(self.content)
        elif not self._check_if_item_in_content(item):
            self.content.append(item)
            ic(self.content)

    @abstractmethod
    def read(self):
        pass

    def _change_attributes(self, old_item, new_item) -> None:
        for attr_name in dir(old_item):
            if not callable(getattr(old_item, attr_name)) and not attr_name.startswith(
                "_"
            ):
                setattr(old_item, attr_name, getattr(new_item, attr_name))

    @abstractmethod
    def update(self, old_item_id: str, new_item: model.Item) -> None:
        old_item = self.find_item(old_item_id)
        if old_item:
            self._change_attributes(old_item, new_item)
        else:
            raise KeyError

    @abstractmethod
    def remove(self, item_to_delete_id: int) -> None:
        content_item = self.find_item(item_to_delete_id)
        if content_item:
            self.content.remove(content_item)
        else:
            raise KeyError


class TxtRepository(AbstractRepository):
    def __init__(self, file: TextIO, type: model.Item) -> None:
        self.item_type: model.Item = type
        self.file: TextIO = file
        self.content: list[model.Item] = None
        self.new_items: list[model.Item] = []
        self.header = None

    def _create_item_instance(self, item_data: dict) -> model.Item:
        item_instace = self.item_type(**item_data)
        return item_instace

    def add(self, item: model.Item) -> None:
        super(TxtRepository, self).add(item)

    def _format_date(self, value: str) -> datetime:
        year, month, day = map(int, value.split("-"))
        return datetime(year, month, day).date()

    def read(self):
        self.content = []
        self.header = self.file.readline()
        keys = self.header.strip().split()
        for line in self.file.readlines():
            values = line.strip().split()
            data = dict(zip(keys, values))
            if "date" in keys:
                data["date"] = self._format_date(data["date"])
            if "distance" in keys:
                data["distance"] = float(data["distance"])
            item_instance = self._create_item_instance(data)
            self.content.append(item_instance)

    def update(self, old_item_id: str, new_item: model.Item):
        super(TxtRepository, self).update(old_item_id, new_item)

    def remove(self, item_to_delete: model.Item):
        super(TxtRepository, self).remove(item_to_delete)


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, item_type: model.Item, session: orm.session) -> None:
        self.item_type = item_type
        self.session: orm.session = session
        self.content: list[model.Item] = None
        self.new_items: list[model.Item] = []

    def read(self) -> None:
        self.content = self.session.query(self.item_type).all()

    def add(self, item: model.Item) -> None:
        super().add(item)
        self.session.add(item)

    def update(self, old_item_id: str, new_item: model.Item):
        old_item = (
            self.session.query(type(new_item)).filter_by(id=int(old_item_id)).first()
        )
        if old_item:
            self._change_attributes(old_item, new_item)
        else:
            raise KeyError
        super().update(old_item_id, new_item)

    def remove(self, item_to_delete_id: int):
        content_item = self.session.get(self.item_type, item_to_delete_id)
        super().remove(item_to_delete_id)
        self.session.delete(content_item)
