from fastapi.testclient import TestClient

import eventcatch.api as api_module
from eventcatch.api import app
from eventcatch.schemas import EventRecord

client = TestClient(app)


def test_extract_endpoint_rejects_empty_text():
    response = client.post("/extract", json={"text": "  "})

    assert response.status_code == 400
    assert "error" in response.json()


def test_extract_endpoint_returns_event(monkeypatch):
    async def fake_extract_and_clean(text: str) -> EventRecord:
        return EventRecord(event_name="Test Event", date="Aug 2")

    monkeypatch.setattr(api_module, "extract_and_clean", fake_extract_and_clean)

    response = client.post("/extract", json={"text": "Test Event Aug 2"})

    assert response.status_code == 200
    body = response.json()
    assert body == {"event_name": "Test Event", "date": "Aug 2"}
