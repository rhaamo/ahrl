import os
import sys
import pytest

mypath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, mypath + "/../")
from app import create_app  # noqa: E402
from models import db as _db  # noqa: E402
from dbseed import seed_config, seed_bands  # noqa: E402
from crons import update_dxcc_from_cty_xml


# Note: this file can't be named with another name than "conftest"


@pytest.yield_fixture(scope="session")
def app():
    cfg = os.getenv("CONFIGTEST", "tests/config_tests.py")
    app = create_app(cfg)
    ctx = app.app_context()
    ctx.push()

    yield app

    ctx.pop()


@pytest.yield_fixture(scope="session")
def db(app):
    _db.drop_all()
    #_db.engine.connect().execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    _db.create_all()

    seed_config(_db)
    seed_bands(_db)

    # Ok here is the joke, if we call update_dxcc_from_cty_xml() with DEBUG=True
    # Everything in the test suite will became extremely slow
    print("import_cty start")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "cty.xml")
    update_dxcc_from_cty_xml(file_path, True)
    print("import_cty end")

    yield _db

    _db.drop_all()


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.yield_fixture(scope="function")
def session(db):
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection)
    session = db.create_scoped_session(options=options)

    db.session = session

    yield session

    transaction.rollback()
    connection.close()
    session.remove()
