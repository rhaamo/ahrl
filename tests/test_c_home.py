def test_home(client, session, app):
    rv = client.get("/")
    assert rv.status_code == 200
    assert b"You can view the following logbook" in rv.data
