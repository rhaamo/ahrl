import json
from os.path import join, dirname


def login(client, email, password):
    return client.post("/login", data=dict(email=email, password=password), follow_redirects=True)


def logout(client):
    return client.get("/logout", follow_redirects=True)


def register(c, email, password, name):
    logout(c)
    resp = c.post(
        "/register",
        data=dict(email=email, password=password, password_confirm=password, name=name),
        follow_redirects=True,
    )
    # should be directly logged
    assert b"Logged as" in resp.data
    assert resp.status_code == 200
    # logout
    logout(c)
    resp = c.get("/")
    assert b"Logged as" not in resp.data
