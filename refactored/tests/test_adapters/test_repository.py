from domain import model
from adapters import repository
from unittest.mock import patch, mock_open
from io import StringIO
from datetime import datetime
from icecream import ic


class Test_TxtRepository:
    def test_read_destinations(self):
        data = """id  name    location    distance
1	DEST-1	LOCATION-1	586
2	DEST-2	LOCATION-2	434
3	DEST-3	LOCATION-3	374"""
        correct_result = [
            str(model.Destination(1, "DEST-1", "LOCATION-1", "586")),
            str(model.Destination(2, "DEST-2", "LOCATION-2", "434")),
            str(model.Destination(3, "DEST-3", "LOCATION-3", "374")),
        ]
        with patch("builtins.open", new_callable=mock_open):
            io_object = StringIO(data)
            txt_repository = repository.TxtRepository(io_object, model.Destination)
            txt_repository.read()
            result = list(map(str, txt_repository.content))
        assert result == correct_result

    def test_read_refuelings(self):
        data = """id    date    volume  destination_id
1\t2023/07/02\t50.0\t1
2\t2023/07/10\t52.0\t1
3\t2023/07/24\t48.0\t1"""
        correct_result = [
            str(model.Refueling("1", datetime(year=2023, month=7, day=2), 50.00, "1")),
            str(model.Refueling("2", datetime(year=2023, month=7, day=10), 52.00, "1")),
            str(model.Refueling("3", datetime(year=2023, month=7, day=24), 48.00, "1")),
        ]
        with patch("builtins.open", new_callable=mock_open):
            io_object = StringIO(data)
            txt_repository = repository.TxtRepository(io_object, model.Refueling)
            txt_repository.read()
            result = list(map(str, txt_repository.content))
        ic(result)
        ic(correct_result)
        assert result == correct_result

    def test_add_successfull(self):
        new_item = model.Destination("4", "DEST-4", "LOCATION-4", "434")
        txt_repository = repository.TxtRepository(StringIO(""), model.Destination)
        txt_repository.content = [
            model.Destination("2", "DEST-2", "LOCATION-2", "434"),
            model.Destination("1", "DEST-1", "LOCATION-1", "586"),
        ]
        txt_repository.add(new_item)
        assert txt_repository.new_items[-1] == new_item

    def test_update(self):
        old_item_id = "1"
        new_item = model.Destination("2", "DEST-2", "LOCATION-2", "434")
        txt_repository = repository.TxtRepository(StringIO(""), model.Destination)
        txt_repository.content = [
            model.Destination("2", "DEST-2", "LOCATION-2", "434"),
            model.Destination("1", "DEST-1", "LOCATION-1", "586"),
        ]
        txt_repository.update(old_item_id, new_item)
        assert str(new_item) == str(txt_repository.content[1])

    def test_delete(self):
        item_to_delete_id = "1"
        txt_repository = repository.TxtRepository(StringIO(""), model.Destination)
        txt_repository.content = [
            model.Destination("2", "DEST-2", "LOCATION-2", "434"),
            model.Destination("1", "DEST-1", "LOCATION-1", "586"),
        ]
        txt_repository.delete(item_to_delete_id)
        assert len(txt_repository.content) == 1 and str(
            txt_repository.content[0]
        ) == str(model.Destination("2", "DEST-2", "LOCATION-2", "434"))
