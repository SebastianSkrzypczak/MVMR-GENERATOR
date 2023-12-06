from services import uow
from domain import model
from unittest.mock import mock_open, patch
import pytest


class Test_TxtUnitOfWork:
    def initial_setup(self):
        destination_uow = uow.TxtUnitOfWork(model.Destination)
        destination_uow.file_path = (
            r"refactored\tests\test_services\TEST_DESTINATIONS.txt"
        )
        correct_result = [
            str(model.Destination("1", "DEST-1", "LOCATION-1", "586")),
            str(model.Destination("4", "DEST-4", "LOCATION-4", "444")),
            str(model.Destination("3", "DEST-3", "LOCATION-3", "374")),
        ]
        old_item_id = "2"
        new_item = model.Destination("4", "DEST-4", "LOCATION-4", "444")

        return destination_uow, correct_result, old_item_id, new_item

    def test_uow_successful_path(self):
        destination_uow, correct_result, old_item_id, new_item = self.initial_setup()

        with open(destination_uow.file_path, "r") as file:
            backup = file.readlines()

        with destination_uow:
            destination_uow.txt_repository.update(old_item_id, new_item)

        with open(destination_uow.file_path, "r") as file:
            result = file.readlines()
            result = result[1:]
            result = [line.strip() for line in result]

        with open(destination_uow.file_path, "w") as file:
            file.writelines(backup)

        assert result == correct_result

    def test_uow_rollback_path(self):
        destination_uow, correct_result, old_item_id, new_item = self.initial_setup()

        old_item_id = "5"

        correct_result = [
            str(model.Destination("1", "DEST-1", "LOCATION-1", "586")),
            str(model.Destination("2", "DEST-2", "LOCATION-2", "434")),
            str(model.Destination("3", "DEST-3", "LOCATION-3", "374")),
        ]

        with open(destination_uow.file_path, "r") as file:
            backup = file.readlines()

        with pytest.raises(StopIteration):
            with destination_uow:
                destination_uow.txt_repository.update(old_item_id, new_item)

        with open(destination_uow.file_path, "r") as file:
            result = file.readlines()
            result = result[1:]
            result = [line.strip() for line in result]

        with open(destination_uow.file_path, "w") as file:
            file.writelines(backup)

        assert result == correct_result
