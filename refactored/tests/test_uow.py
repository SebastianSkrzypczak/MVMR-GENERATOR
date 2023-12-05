from services import uow
from domain import model
from icecream import ic
from unittest.mock import mock_open, patch


class Test_TxtUnitOfWork:
    def test_uow_update_successful(self):
        destination_uow = uow.TxtUnitOfWork(model.Destination)
        data = """id  name    location    distance
1	DEST-1	LOCATION-1	586
2	DEST-2	LOCATION-2	434
3	DEST-3	LOCATION-3	374"""
        correct_result = [
            str(model.Destination("1", "DEST-1", "LOCATION-1", "586")),
            str(model.Destination("1", "DEST-1", "LOCATION-1", "586")),
            str(model.Destination("3", "DEST-3", "LOCATION-3", "374")),
        ]
        old_item_id = "2"
        new_item = model.Destination("1", "DEST-1", "LOCATION-1", "586")
        with patch("builtins.open", mock_open(read_data=data)):
            with destination_uow:
                ic(destination_uow.txt_repository.content)
                ic(old_item_id)
                destination_uow.txt_repository.update(old_item_id, new_item)
                result = [str(item) for item in destination_uow.txt_repository.content]
                assert result == correct_result

    def test_uow_commit_successful(self):
        pass
