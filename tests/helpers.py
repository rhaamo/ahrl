import os
from bs4 import BeautifulSoup as bs
import re


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


def update_profile(client, callsign, locator):
    return client.post("/user/edit", follow_redirects=True, data=dict(callsign=callsign, locator=locator))


def add_contact(client, callsign, locator):
    return client.post("/contacts/new", data=dict(callsign=callsign, gridsquare=locator), follow_redirects=True)


_contacts_reg = re.compile(r"/contacts/(\d+)/edit")


def get_contact_id(html, callsign):
    soup = bs(html, 'html.parser')
    table = soup.find('table', {'class': 'contacts-list'})
    rows = table.findAll('tr')
    row = next(t for t in rows if t.findAll(text=re.compile(callsign)))
    href = row.findAll('a', href=re.compile('edit'))
    assert len(href) > 0
    href = href[0]['href']
    match = _contacts_reg.search(href)
    assert match
    assert len(match.groups()) >= 1
    return match.group(1)
