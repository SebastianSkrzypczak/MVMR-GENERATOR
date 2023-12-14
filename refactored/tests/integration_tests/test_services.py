from domain import model
from services import uow, logic
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from icecream import ic
from adapters import orm


class Test_Mvmr_with_txt_uow:
    def test_generate_mvmr(self):
        destinations_uow = uow.TxtUnitOfWork(model.Destination)
        refuelings_uow = uow.TxtUnitOfWork(model.Refueling)

        with destinations_uow:
            with refuelings_uow:
                mvmr = logic.Mvmr(
                    destinations_uow.repository,
                    refuelings_uow.repository,
                    7,
                    2023,
                    1000,
                    0,
                )
        mvmr.generate_random()

        assert 1 == 1


class Test_Mvmr_with_sql_uow:
    def initial_data(self):
        destinations_uow = uow.TxtUnitOfWork(model.Destination)
        refuelings_uow = uow.TxtUnitOfWork(model.Refueling)
        destinations = []
        refuelings = []

        with destinations_uow:
            for destination in destinations_uow.repository.content:
                destinations.append(destination)

        with refuelings_uow:
            for refueling in refuelings_uow.repository.content:
                refuelings.append(refueling)

        return destinations, refuelings

    def test_generate_mvmr(self):
        orm.start_mappers()
        engine = create_engine("sqlite:///:memory:")
        orm.metadata.create_all(engine)

        session_factory = sessionmaker(bind=engine)

        destinations_uow = uow.SqlAlchemyUnitOfWork(model.Destination, session_factory)
        refuelings_uow = uow.SqlAlchemyUnitOfWork(model.Refueling, session_factory)

        destinations, refuelings = self.initial_data()

        with destinations_uow:
            with refuelings_uow:
                for destination in destinations:
                    destinations_uow.repository.add(destination)
                for refueling in refuelings:
                    refuelings_uow.repository.add(refueling)

                mvmr = logic.Mvmr(
                    destinations_uow.repository,
                    refuelings_uow.repository,
                    7,
                    2023,
                    1000,
                    0,
                )
        mvmr.generate_random()

        # TODO: testing sqlrepo

        assert 1 == 1
