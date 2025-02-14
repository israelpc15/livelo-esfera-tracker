import json
from app.services.restapi_class import RestApiClient

# A dummy response class to simulate requests responses.
class DummyResponse:
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception("Bad status")

    def json(self):
        return self._json_data

    @property
    def text(self):
        return json.dumps(self._json_data)

def test_get(monkeypatch):
    def dummy_get(url, params, headers):
        # Assert that the URL contains a known substring
        assert "test_endpoint" in url
        assert params == {"key": "value"}
        return DummyResponse({"result": "success"}, 200)
    monkeypatch
