import helpers
from models import db, User


def test_login_logout(client, session):
    """Make sure login and logout works."""

    helpers.register(client, "dashie@sigpipe.me", "fluttershy", "UserTLL")

    rv = helpers.login(client, "dashie@sigpipe.me", "fluttershy")
    assert rv.status_code == 200
    assert b"Logged as UserTLL" in rv.data

    rv = helpers.logout(client)
    assert rv.status_code == 200
    assert b"Logged as UserTLL" not in rv.data

    rv = helpers.login(client, "dashie@sigpipe.me" + "x", "fluttershy")
    assert rv.status_code == 200
    assert b"Specified user does not exist" in rv.data

    rv = helpers.login(client, "dashie@sigpipe.me", "fluttershy" + "x")
    assert rv.status_code == 200
    assert b"Invalid password" in rv.data


def test_registration(client, session, app):
    helpers.register(client, "dashie+tr@sigpipe.me", "fluttershy", "UserTR")


def test_user_in_bdd(client, session):
    helpers.register(client, "dashie+tuib@sigpipe.me", "fluttershy", "UserTUIB")
    a = User.query.filter(User.name == "UserTUIB").first()
    assert a is not None


def test_count_user(client, session):
    a = User.query.all()
    assert len(a) > 0


def test_not_logged_user(client, session):
    rv = client.get("/user", follow_redirects=True)
    assert b"Please log in to access this page." in rv.data


def test_logging_user(client, session):
    helpers.register(client, "dashie+tlu@sigpipe.me", "fluttershy", "UserTLU")
    helpers.login(client, "dashie+tlu@sigpipe.me", "fluttershy")
    rv = client.get("/user", follow_redirects=True)
    assert b"dashie+tlu@sigpipe.me" in rv.data
    helpers.logout(client)
    assert b"Logged as UserTLU" in rv.data


# Profile
def test_profile(client, session):
    helpers.register(client, "dashie+tp@sigpipe.me", "fluttershy", "UserTP")
    helpers.login(client, "dashie+tp@sigpipe.me", "fluttershy")
    rv = client.get("/user", follow_redirects=True)
    assert b"Please fill me !" in rv.data
    assert b"Please fill me !" in rv.data
    helpers.logout(client)


def test_profile_edit(client, session):
    helpers.register(client, "dashie+tpe@sigpipe.me", "fluttershy", "UserTPE")
    helpers.login(client, "dashie+tpe@sigpipe.me", "fluttershy")
    rv = helpers.update_profile(client, "N0CALL", "JN18CX")
    assert b"<td>N0CALL</td>" in rv.data
    assert b"<td>JN18CX</td>" in rv.data


def test_nonexist_user(client, session, app):
    rv = client.get("/user/davenull/logbook/1-test", follow_redirects=True)
    assert b"User not found" in rv.data
