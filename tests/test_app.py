from flask_testing import TestCase
from app import create_app
from nose2.compat import unittest
# import sys
# sys.path.insert(0, sys.path[0] + '/../')

from models import db, User, user_datastore, Role
from dbseed import seed_config, seed_bands


class TestViews(TestCase):
    def create_app(self):
        cfg = {'SQLALCHEMY_DATABASE_URI': "postgresql+psycopg2://dashie:saucisse@localhost/ahrl_tests",
               'DEBUG_TB_PROFILER_ENABLED': False,
               'SECURITY_REGISTERABLE': True,
               'WTF_CSRF_CHECK_DEFAULT': False,
               'CSRF_ENABLED': False,
               'WTF_CSRF_ENABLED': False}
        app = create_app(cfg)
        return app

    def setUp(self):
        db.create_all()
        seed_config(db)
        seed_bands(db)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def register(self):
        return self.client.post('/register',
                                data=dict(email='dashie@sigpipe.me',
                                          name='dashie', password='fluttershy', password_confirm='fluttershy'),
                                follow_redirects=True)

    def login(self):
        return self.client.post('/login',
                                data=dict(email='dashie@sigpipe.me', password='fluttershy'),
                                follow_redirects=True)

    def logout(self):
        return self.client.post('/logout', follow_redirects=True)

    # Test main app
    def test_home(self):
        rv = self.client.get("/")
        self.assertIn(b"You can view the following logbook", rv.data)

    def test_registration(self):
        rv = self.register()
        self.assertIn(b"Logged as dashie", rv.data)

    def test_user_in_bdd(self):
        self.register()
        a = User.query.filter(User.name == 'dashie').first()
        self.assertIsNotNone(a)

    def test_count_user(self):
        a = User.query.all()
        self.assertEqual(len(a), 0)

    def test_not_logged_user(self):
        rv = self.client.get("/user", follow_redirects=True)
        self.assertIn(b"Please log in to access this page.", rv.data)

    def test_logging_user(self):
        self.register()
        self.login()
        rv = self.client.get("/user", follow_redirects=True)
        self.assertIn(b"dashie@sigpipe.me", rv.data)
        self.logout()
        self.assertIn(b"Logged as dashie", rv.data)

    def test_profile(self):
        self.register()
        self.login()
        rv = self.client.get("/user", follow_redirects=True)
        self.assertIn(b"Please fill me !", rv.data)
        self.assertIn(b"Please fill me !", rv.data)
        self.logout()

    # Todo test profile edit

    #def add_contact(self, call, loc):
    #    return self.client.post('/login',
    #                            data=dict(email='dashie@sigpipe.me', password='fluttershy'),
    #                            follow_redirects=True)

    #def test_add_contact(self):
    #    self.register()
    #    self.login()
    #    rv = self.add_contact("F4TEST", "JN1742")

if __name__ == '__main__':
    unittest.main()
