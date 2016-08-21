from flask_testing import TestCase
from app import create_app
from models import db
from nose2.compat import unittest


class TestViews(TestCase):
    def create_app(self):
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://dashie:saucisse@localhost/ahrl_tests"
        app.config['DEBUG_TB_PROFILER_ENABLED'] = False
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # Test main app
    def test_home(self):
        rv = self.client.get("/")
        assert b"You can view the following logbook" in rv.data

if __name__ == '__main__':
    unittest.main()