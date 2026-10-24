from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health/check")
    assert response.status_code == 200


def test_health_db():
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json() == {"db": "ok"}
