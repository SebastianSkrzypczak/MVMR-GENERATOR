from services import uow
from domain import model
from adapters import repository
from auth import auth
import os


def load_data_from_txt_file(
    file_name: str, type: model.Item
) -> repository.TxtRepository:
    file_path = os.path.join("files", file_name)
    with open(file_path, "r") as file:
        txt_repository = repository.TxtRepository(file, type)
        txt_repository.read()
    return txt_repository


def save_data_with_uow(
    uow: uow.AbstractUnitOfWork, repostiory: repository.AbstractRepository
) -> None:
    with uow:
        for item in repostiory.content:
            uow.repository.add(item)
        uow.commit()


def remove_many_with_uow(
    uow: uow.AbstractUnitOfWork, items_to_delete: list[str]
) -> None:
    with uow:
        for item_id in items_to_delete:
            uow.repository.remove(int(item_id))
        uow.commit()


def get_content_with_uow(uow: uow.AbstractUnitOfWork) -> list[model.Item]:
    with uow:
        content = uow.repository.content
    return content


def find_item_by_id_with_uow(uow: uow.AbstractUnitOfWork, id: int) -> model.Item:
    with uow:
        item = uow.repository.find_item(id)
    return item


def get_last_id_with_uow(uow: uow.AbstractUnitOfWork) -> int:
    with uow:
        last_id = uow.get_last_id()
    return last_id


def add_with_uow(uow: uow.AbstractUnitOfWork, item: model.Item) -> None:
    with uow:
        uow.repository.add(item)
        print(uow.repository.content)
        uow.commit()


def update_with_uow(uow: uow.AbstractUnitOfWork, id: int, item: model.Item) -> None:
    with uow:
        uow.repository.update(id, item)
        uow.commit()


def find_user_by_username(
    uow: uow.AbstractUnitOfWork, username: str
) -> auth.User | None:
    with uow:
        found_user = next(
            user for user in uow.repository.content if username == user.username
        )
        if found_user:
            return found_user
        else:
            return None


def authenicate_user(
    uow: uow.AbstractUnitOfWork, username: str, password: str
) -> auth.User | None:
    user: auth.User = find_user_by_username(uow, username)
    if user.check_password(password):
        return user
    else:
        return None
