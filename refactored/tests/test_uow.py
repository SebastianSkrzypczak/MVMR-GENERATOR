from services import uow
from domain import model
from icecream import ic
from unittest.mock import mock_open, patch


class Test_TxtUnitOfWork:
    def test_uow_read_successful(self):
        destination_uow = uow.TxtUnitOfWork(model.Destination)
        data = """id  name    location    distance
1	DEST-1	LOCATION-1	586
2	DEST-2	LOCATION-2	434
3	DEST-3	LOCATION-3	374"""
        correct_result = [
            str(model.Destination(1, "DEST-1", "LOCATION-1", "586")),
            str(model.Destination(2, "DEST-2", "LOCATION-2", "434")),
            str(model.Destination(3, "DEST-3", "LOCATION-3", "374")),
        ]
        with patch("builtins.open", mock_open(read_data=data)):
            with destination_uow:
                ic(destination_uow.txt_repository.content)
                result = [str(item) for item in destination_uow.txt_repository.content]
                assert result == correct_result
