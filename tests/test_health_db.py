def test_health_check(client):
    response = client.get("/health/check")
    assert response.status_code == 200


def test_health_db(client):
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json() == {"db": "ok"}
