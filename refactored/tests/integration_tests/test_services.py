from domain import model
from services import uow, logic
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from icecream import ic
from adapters import orm
from config import get_settings_for_random_generation
import statistics


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
        mvmr.get_work_days_in_month()
        mvmr.add_refuelings_to_trips()
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
        mvmr.get_work_days_in_month()
        mvmr.add_refuelings_to_trips()
        mvmr.generate_random()

        ic([(trip.destination.name, trip.milage) for trip in mvmr.trips])

        assert 1 == 1

    def test_generate_mvmr_accuracy(self):
        engine = create_engine("sqlite:///:memory:")
        orm.metadata.create_all(engine)

        session_factory = sessionmaker(bind=engine)

        destinations_uow = uow.SqlAlchemyUnitOfWork(model.Destination, session_factory)
        refuelings_uow = uow.SqlAlchemyUnitOfWork(model.Refueling, session_factory)

        destinations, refuelings = self.initial_data()

        differences = []

        with destinations_uow:
            with refuelings_uow:
                for destination in destinations:
                    destinations_uow.repository.add(destination)
                for refueling in refuelings:
                    refuelings_uow.repository.add(refueling)

                for _ in range(0, 100):
                    mvmr = logic.Mvmr(
                        destinations_uow.repository,
                        refuelings_uow.repository,
                        7,
                        2023,
                        1000,
                        0,
                    )
                    mvmr.get_work_days_in_month()
                    mvmr.add_refuelings_to_trips()
                    mvmr.generate_random()
                    difference = 1000 - mvmr.trips[-1].milage
                    differences.append(difference)

        max_difference = get_settings_for_random_generation().get("max_difference")

        assert statistics.mean(differences) <= max_difference
