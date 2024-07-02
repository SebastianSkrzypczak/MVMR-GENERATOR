import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from adapters import orm


@pytest.fixture(scope="session")
def engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="session")
def tables(engine):
    orm.start_mappers(engine)
    orm.metadata.create_all(engine)
    yield

    orm.metadata.drop_all(engine)
    clear_mappers()


@pytest.fixture
def session(engine, tables):

    Session = sessionmaker(bind=engine)
    session = Session()
    yield session

    session.close()
    clear_mappers()
