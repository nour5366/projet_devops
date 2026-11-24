def creer(client, data):
    return client.post("/incidents/new", data=data)


def test_ajout_incident(client, incident_data):
    r = creer(client, incident_data)
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/incidents/1")


def test_liste_retournee(client, incident_data):
    creer(client, incident_data)
    r = client.get("/api/incidents")
    assert r.status_code == 200
    assert len(r.json) == 1
    assert r.json[0]["titre"] == "Projecteur HS"
    assert r.json[0]["statut"] == "nouveau"
    assert "Projecteur HS" in client.get("/incidents").get_data(as_text=True)


def test_detail_incident(client, incident_data):
    creer(client, incident_data)
    r = client.get("/incidents/1")
    assert r.status_code == 200
    assert "Salle B12" in r.get_data(as_text=True)
    assert client.get("/incidents/999").status_code == 404


def test_modifier_statut(client, incident_data):
    creer(client, incident_data)
    r = client.post("/incidents/1/statut", data={"statut": "resolu"})
    assert r.status_code == 302
    assert client.get("/api/incidents").json[0]["statut"] == "resolu"
    assert client.post("/incidents/1/statut", data={"statut": "inconnu"}).status_code == 400


def test_supprimer_incident(client, incident_data):
    creer(client, incident_data)
    client.post("/incidents/1/delete")
    assert client.get("/api/incidents").json == []


def test_incident_invalide_refuse(client):
    r = creer(client, {"titre": "", "description": "x", "lieu": "", "priorite": "urgent"})
    assert r.status_code == 400
    assert client.get("/api/incidents").json == []
