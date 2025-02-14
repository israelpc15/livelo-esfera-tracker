import datetime
from app.watchstore_class import WatchStore

def test_from_dict():
    data = {
         "code": "MOV",
         "name": "Movida",
         "valid_until": "2022-11-30",
         "min_points": 8,
         "categories": ["films", "music"]
    }
    ws = WatchStore.from_dict(data)
    assert ws.code == "MOV"
    assert ws.name == "Movida"
    # Check that the date was parsed correctly
    assert ws.valid_until == datetime.datetime.strptime("2022-11-30", "%Y-%m-%d").date()
    assert ws.min_points == 8
    assert ws.categories == ["films", "music"]

def test_is_valid():
    # Test with a future date (store should be valid)
    future_date = (datetime.date.today() + datetime.timedelta(days=10)).strftime('%Y-%m-%d')
    ws_future = WatchStore("TEST", "Test Store", future_date, 5)
    assert ws_future.is_valid() is True

    # Test with a past date (store should be invalid)
    past_date = (datetime.date.today() - datetime.timedelta(days=10)).strftime('%Y-%m-%d')
    ws_past = WatchStore("TEST", "Test Store", past_date, 5)
    assert ws_past.is_valid() is False
