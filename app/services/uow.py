from adapters import repository
from abc import ABC, abstractmethod
from domain import model
from sqlalchemy.orm import sessionmaker, session
from icecream import ic
from sqlalchemy import inspect
import config
from sqlalchemy import func


class AbstractUnitOfWork(ABC):
    @abstractmethod
    def __enter__(self):
        return self

    @abstractmethod
    def __exit__(self, exttype: Exception, exc_value, traceback):
        pass

    @abstractmethod
    def rollback(self, content: list):
        pass

    @abstractmethod
    def commit(self, content: list):
        pass

    @abstractmethod
    def get_last_id(self, item: model.Item):
        pass


class TxtUnitOfWork(AbstractUnitOfWork):
    def __init__(self, item_type: model.Item) -> None:
        self.item_type: model.Item = item_type
        self.file_path = rf"refactored\files\{str(item_type.__name__).upper()}S.txt"
        self.backup_content: list[model.Item] = None
        self.repository: repository.AbstractRepository = None

    def __enter__(self):
        with open(self.file_path, "r", encoding="unicode") as file:
            if not self.repository:
                self.repository = repository.TxtRepository(file, self.item_type)
            self.repository.read()
            self.backup_content = self.repository.content

    def commit(self):
        new_content = []
        for item in self.repository.content:
            new_content.append(str(item))
        with open(self.file_path, "w", encoding="unicode") as file:
            file.write(self.repository.header)
            file.writelines(line + "\n" for line in new_content)

    def rollback(self):
        self.repository.content = self.backup_content
        self.commit()

    def __exit__(self, exttype: Exception, exc_value, traceback):
        if not exttype:
            if self.repository.new_items:
                self.repository.content.append(self.repository.new_items)
            self.commit()
        else:
            self.rollback()

    def get_last_id(self, item: model.Item):
        return super().get_last_id(item)


DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=config.create_db_engine(),
    expire_on_commit=False,
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(
        self, item_type: model.Item, session_factory=DEFAULT_SESSION_FACTORY
    ) -> None:
        self.item_type = item_type
        self.sesion_factory = session_factory
        self.backup_content = None
        self.repository = None
        self.session = None

    def __enter__(self):
        self.session = self.sesion_factory()  # type: session.Session
        if not self.repository:
            self.repository = repository.SqlAlchemyRepository(
                self.item_type, self.session
            )
            self.repository.read()
        else:
            self.repository.session = None
            self.repository.session = self.session

        return super().__enter__()

    def __exit__(self, exttype: Exception, exc_value, traceback):
        if exttype is not None:
            self.session.rollback()
        self.session.close()

    def rollback(self):
        self.session.rollback()

    def commit(self):
        self.session.commit()

    def table_exist(self, table_name):
        inspector = inspect(self.session.bind)
        return inspector.has_table(table_name)

    def get_last_id(self):
        last_id = self.session.query(func.max(self.item_type.id)).scalar() or 0
        return last_id
