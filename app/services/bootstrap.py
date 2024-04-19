from services import uow
from domain import model
from adapters import orm


def bootstrap(
    start_orm: bool = True,
    destination_uow: uow.AbstractUnitOfWork = uow.SqlAlchemyUnitOfWork(
        model.Destination
    ),
    cars_uow: uow.AbstractUnitOfWork = uow.SqlAlchemyUnitOfWork(model.Car),
    refueling_uow: uow.AbstractUnitOfWork = uow.SqlAlchemyUnitOfWork(model.Refueling),
    trips_uow: uow.AbstractUnitOfWork = uow.SqlAlchemyUnitOfWork(model.Trip),
) -> uow.AbstractUnitOfWork:

    if start_orm:
        orm.start_mappers()

    return (
        cars_uow,
        destination_uow,
        refueling_uow,
        trips_uow,
    )