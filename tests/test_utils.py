from utils import gen_random_str
from models import db, DxccPrefixes, DxccExceptions, DxccEntities


def test_debug_testing(app):
    """
    For some reasons, the tests will be EXTREMELY SLOW if DEBUG=True
    I have no effing idea why.
    See conftest.py:db() for more.
    """
    assert not app.config["DEBUG"]
    assert app.config["TESTING"]


def test_gen_random_str():
    times = 0
    while True:
        a = gen_random_str(20)
        b = gen_random_str(20)
        assert a != b
        times += 1
        if times >= 100:
            break


def test_import_xml_offline(client, session, app):
    # This test rely on import_cty() called in db() of conftest
    _dp = db.session.query(DxccPrefixes.id).count()
    _dx = db.session.query(DxccExceptions.id).count()
    _de = db.session.query(DxccEntities.id).count()
    # Count as of 25/08/16 was:
    # 3665     16435     401
    # check are lowered to avoid changing them maybe too frequently
    assert _dp >= 3500
    assert _dx >= 16300
    assert _de >= 300
