from flask_testing import TestCase
from app import create_app

from models import db, User, DxccPrefixes, DxccExceptions, DxccEntities
from dbseed import seed_config, seed_bands
from crons import update_dxcc_from_cty_xml


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

    def import_cty(self):
        update_dxcc_from_cty_xml(self.app.config['TEMP_DOWNLOAD_FOLDER'] + "/../tests/cty.xml", True)

    # Test cty.xml import
    def test_010_import_xml_offline(self):
        self.import_cty()
        _dp = db.session.query(DxccPrefixes.id).count()
        _dx = db.session.query(DxccExceptions.id).count()
        _de = db.session.query(DxccEntities.id).count()
        # Count as of 25/08/16 was:
        # 3665     16435     401
        # check are lowered to avoid changing them maybe too frequently
        self.assertGreaterEqual(_dp, 3500)
        self.assertGreaterEqual(_dx, 16300)
        self.assertGreaterEqual(_de, 300)

    # Test main app
    def test_020_home(self):
        self.import_cty()
        rv = self.client.get("/")
        self.assertIn(b"You can view the following logbook", rv.data)

    def test_030_registration(self):
        self.import_cty()
        rv = self.register()
        self.assertIn(b"Logged as dashie", rv.data)

    def test_040_user_in_bdd(self):
        self.register()
        a = User.query.filter(User.name == 'dashie').first()
        self.assertIsNotNone(a)

    def test_050_count_user(self):
        a = User.query.all()
        self.assertEqual(len(a), 0)

    def test_060_not_logged_user(self):
        rv = self.client.get("/user", follow_redirects=True)
        self.assertIn(b"Please log in to access this page.", rv.data)

    def test_070_logging_user(self):
        self.register()
        self.login()
        rv = self.client.get("/user", follow_redirects=True)
        self.assertIn(b"dashie@sigpipe.me", rv.data)
        self.logout()
        self.assertIn(b"Logged as dashie", rv.data)

    # Profile
    def test_080_profile(self):
        self.register()
        self.login()
        rv = self.client.get("/user", follow_redirects=True)
        self.assertIn(b"Please fill me !", rv.data)
        self.assertIn(b"Please fill me !", rv.data)
        self.logout()

    def update_profile(self):
        return self.client.post("/user/edit", follow_redirects=True, data=dict(
            callsign="N0CALL", locator="JN18CX"
        ))

    def test_090_profile_edit(self):
        self.register()
        self.login()
        rv = self.update_profile()
        self.assertIn(b"<td>N0CALL</td>", rv.data)
        self.assertIn(b"<td>JN18CX</td>", rv.data)

    # Contacts
    def add_contact(self, call, loc):
        return self.client.post('/contacts/new',
                                data=dict(callsign=call, gridsquare=loc),
                                follow_redirects=True)

    def test_100_add_contact(self):
        self.register()
        self.login()
        self.update_profile()
        rv = self.add_contact("F4TEST", "JN11DW")
        self.assertIn(b"<td>F4TEST</td>", rv.data)
        self.assertIn(b"<td>783.0 Km</td>", rv.data)
        self.assertIn(b"<td>179.0</td>", rv.data)
        self.assertIn(b"<td>S</td>", rv.data)

    def test_110_add_contact_no_locator(self):
        self.register()
        self.login()
        rv = self.add_contact("F4TEST", "JN11DW")
        self.assertIn(b"Missing locator_qso or locator_user", rv.data)

    def test_120_edit_contact(self):
        self.register()
        self.login()
        self.update_profile()
        self.add_contact("F4TEST", "JN11DW")
        rv = self.client.post("/contacts/1/edit", follow_redirects=True, data=dict(callsign="F8COIN",
                                                                                   gridsquare="JN11DW"))
        self.assertIn(b"<td>F8COIN</td>", rv.data)
        self.assertIn(b"<td>783.0 Km</td>", rv.data)
        self.assertIn(b"<td>179.0</td>", rv.data)
        self.assertIn(b"<td>S</td>", rv.data)

    def test_130_delete_contact(self):
        self.register()
        self.login()
        self.update_profile()
        self.add_contact("F4TEST", "JN11DW")
        rv = self.client.get('/contacts/1/delete')
        self.assertNotIn(b"<td>F4TEST</td>", rv.data)
        self.assertNotIn(b"<td>783.0 Km</td>", rv.data)
        self.assertNotIn(b"<td>179.0</td>", rv.data)
        self.assertNotIn(b"<td>S</td>", rv.data)

    def test_140_add_contact_missing_locator(self):
        self.register()
        self.login()
        self.update_profile()
        rv = self.client.post('/contacts/new',
                              data=dict(callsign="F4TEST"),
                              follow_redirects=True)
        self.assertIn(b"QTH is too broad or empty, please input valid QTH", rv.data)

    def test_150_add_contact_missing_call(self):
        self.register()
        self.login()
        self.update_profile()
        rv = self.client.post('/contacts/new',
                              data=dict(gridsquare="JN18CX"),
                              follow_redirects=True)
        self.assertIn(b"This field is required.", rv.data)

    # Notes

    # Logbooks

    # Non existent
    def test_160_nonexist_user(self):
        self.import_cty()
        rv = self.client.get('/user/davenull/logbook/1-test', follow_redirects=True)
        self.assertIn(b"User not found", rv.data)

    def test_170_nonexist_logbook(self):
        self.register()
        rv = self.client.get('/user/dashie/logbook/1-test', follow_redirects=True)
        self.assertIn(b"Logbook not found", rv.data)

        # QSOs

        # JSons and APIs

        # Adif import / export
