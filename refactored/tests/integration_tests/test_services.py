from domain import model
from services import uow, logic
from adapters import repository
from icecream import ic


class TestMvmr:
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
                    0,
                    0,
                )

        ic(mvmr.available_days)

        assert 1 == 0
