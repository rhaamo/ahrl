import helpers


def test_add_contact(client, session):
    helpers.register(client, "dashie+tac@sigpipe.me", "fluttershy", "UserTAC")
    helpers.login(client, "dashie+tac@sigpipe.me", "fluttershy")
    helpers.update_profile(client, "F0COIN", "JN18CX")
    rv = helpers.add_contact(client, "F4TEST", "JN11DW")
    assert b"<td>F4TEST</td>" in rv.data
    assert b"<td>783.0 Km</td>" in rv.data
    assert b"<td>179.0</td>" in rv.data
    assert b"<td>S</td>" in rv.data


def test_add_contact_no_locator(client, session):
    helpers.register(client, "dashie+tacnl@sigpipe.me", "fluttershy", "UserTACNL")
    helpers.login(client, "dashie+tacnl@sigpipe.me", "fluttershy")
    rv = helpers.add_contact(client, "F4TEST", "JN11DW")
    assert b"Missing locator_qso or locator_user" in rv.data


def test_edit_contact(client, session):
    helpers.register(client, "dashie+tec@sigpipe.me", "fluttershy", "UserTEC")
    helpers.login(client, "dashie+tec@sigpipe.me", "fluttershy")
    helpers.update_profile(client, "F8TEST", "JN18CX")
    rv = helpers.add_contact(client, "F4TEST", "JN11DW")
    contact_id = helpers.get_contact_id(rv.data, "F4TEST")
    rv = client.post(
        f"/contacts/{contact_id}/edit", follow_redirects=True, data=dict(callsign="F8COIN", gridsquare="JN11DW")
    )
    assert b"<td>F8COIN</td>" in rv.data
    assert b"<td>783.0 Km</td>" in rv.data
    assert b"<td>179.0</td>" in rv.data
    assert b"<td>S</td>" in rv.data


def test_delete_contact(client, session):
    helpers.register(client, "dashie+tdc@sigpipe.me", "fluttershy", "UserTDC")
    helpers.login(client, "dashie+tdc@sigpipe.me", "fluttershy")
    helpers.update_profile(client, "F4JFD", "JN18CX")
    rv = helpers.add_contact(client, "F4TEST", "JN11DW")
    contact_id = helpers.get_contact_id(rv.data, "F4TEST")
    rv = client.get(f"/contacts/{contact_id}/delete")
    assert b"<td>F4TEST</td>" not in rv.data
    assert b"<td>783.0 Km</td>" not in rv.data
    assert b"<td>179.0</td>" not in rv.data
    assert b"<td>S</td>" not in rv.data


def test_add_contact_missing_locator(client, session):
    helpers.register(client, "dashie+tacml@sigpipe.me", "fluttershy", "UserTACML")
    helpers.login(client, "dashie+tacml@sigpipe.me", "fluttershy")
    helpers.update_profile(client, "F4JFD", "JN09CX")
    rv = client.post("/contacts/new", data=dict(callsign="F4TEST"), follow_redirects=True)
    assert b"QTH is too broad or empty, please input valid QTH" in rv.data


def test_add_contact_missing_call(client, session):
    helpers.register(client, "dashie+tacmc@sigpipe.me", "fluttershy", "UserTACMC")
    helpers.login(client, "dashie+tacmc@sigpipe.me", "fluttershy")
    helpers.update_profile(client, "F4JFD", "JN09CX")
    rv = client.post("/contacts/new", data=dict(gridsquare="JN18CX"), follow_redirects=True)
    assert b"This field is required." in rv.data
