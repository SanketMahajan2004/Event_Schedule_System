import pytest
from app import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_create_event(client):
    response = client.post("/events", json={
        "title": "Meeting",
        "description": "Project discussion",
        "start_time": "2025-07-01T10:00:00",
        "end_time": "2025-07-01T11:00:00"
    })
    assert response.status_code == 201
    assert "event" in response.json
