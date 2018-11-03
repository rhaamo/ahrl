import helpers


def test_nonexist_logbook(client, session):
    helpers.register(client, "dashie+tnl@sigpipe.me", "fluttershy", "UserTNL")
    rv = client.get("/user/UserTNL/logbook/1-test", follow_redirects=True)
    assert b"Logbook not found" in rv.data
