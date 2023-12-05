from domain import model
from adapters import repository
from unittest.mock import patch, mock_open
from io import StringIO


class Test_TxtRepository:
    def test_read(self):
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
