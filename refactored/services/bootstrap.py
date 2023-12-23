from services import logic, uow
from domain import model
from adapters import orm


def bootstrap(
    start_orm: bool = True,
    destination_uow: uow.AbstractUnitOfWork = uow.SqlAlchemyUnitOfWork(
        model.Destination
    ),
    refueling_uow: uow.AbstractUnitOfWork = uow.SqlAlchemyUnitOfWork(model.Refueling),
) -> uow.AbstractUnitOfWork:
    if start_orm:
        orm.start_mappers()

    return destination_uow, refueling_uow
