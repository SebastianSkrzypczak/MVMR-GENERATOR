from adapters import repository
from abc import ABC, abstractmethod
from domain import model
from sqlalchemy.orm import sessionmaker, session
from sqlalchemy import create_engine, inspect
import config


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


class TxtUnitOfWork(AbstractUnitOfWork):
    def __init__(self, item_type: model.Item):
        self.item_type = item_type
        self.file_path = rf"refactored\files\{str(item_type.__name__).upper()}S.txt"
        self.backup_content = None
        self.repository = None

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


DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(
        config.get_postgres_uri(),
        isolation_level="REPEATABLE READ",
    )
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
        return super().__enter__()

    def __exit__(self, exttype: Exception, exc_value, traceback):
        self.session.close()

    def rollback(self):
        self.session.rollback()

    def commit(self):
        self.session.commit()

    def table_exist(self, table_name):
        inspector = inspect(self.session.bind)
        return inspector.has_table(table_name)
