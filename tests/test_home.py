def test_home_accessible(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Incidents" in r.get_data(as_text=True)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json["status"] == "OK"
