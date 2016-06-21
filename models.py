from flask_sqlalchemy import SQLAlchemy
from flask_security import SQLAlchemyUserDatastore, UserMixin, RoleMixin

from sqlalchemy.sql import func
from sqlalchemy_searchable import make_searchable

from libqth import is_valid_qth, qth_to_coords, coords_to_qth
from geohelper import distance

import datetime

db = SQLAlchemy()
make_searchable()


roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, info={'label': 'Name'})
    description = db.Column(db.String(255), info={'label': 'Description'})

    __mapper_args__ = {"order_by": name}


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, info={'label': 'Email'})
    name = db.Column(db.String(255), unique=True, nullable=False, info={'label': 'Name'})
    password = db.Column(db.String(255), nullable=False, info={'label': 'Password'})
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())

    callsign = db.Column(db.String(32))
    locator = db.Column(db.String(16))
    firstname = db.Column(db.String(32))
    lastname = db.Column(db.String(32))
    lotw_name = db.Column(db.String(32))
    lotw_password = db.Column(db.String(255))
    eqsl_name = db.Column(db.String(32))
    eqsl_password = db.Column(db.String(255))
    timezone = db.Column(db.String(255), nullable=False)  # Managed and fed by pytz
    swl = db.Column(db.Boolean(), nullable=False, default=False)
    zone = db.Column(db.String(10), nullable=False, default='iaru1')

    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    logbooks = db.relationship('Logbook', backref='user', lazy='dynamic')
    logs = db.relationship('Log', backref='user', lazy='dynamic')
    notes = db.relationship('Note', backref='user', lazy='dynamic')
    apitokens = db.relationship('Apitoken', backref='user', lazy='dynamic')
    contacts = db.relationship('Contact', backref='user', lazy='dynamic')

    user_loggings = db.relationship('UserLogging', backref='user', lazy='dynamic')
    loggings = db.relationship('Logging', backref='user', lazy='dynamic')

    __mapper_args__ = {"order_by": name}

    def join_roles(self, string):
        return string.join([i.description for i in self.roles])

    def qth_to_coords(self):
        qth = is_valid_qth(self.locator, 6)
        if not qth:
            return None
        qth = qth_to_coords(self.locator, 6)
        if not qth:
            return None
        return qth

    # Give a cute name <3 More like "name - callsign" or "callsign"
    def cutename(self):
        cute = ""
        if self.name:
            cute += self.name
            cute += " - "
        cute += self.callsign
        return cute

    def zone_str(self):
        if self.zone == 'iaru1':
            return 'IARU Zone 1'
        elif self.zone == 'iaru2':
            return 'IARU Zone 2'
        elif self.zone == 'iaru3':
            return 'IARU Zone 3'
        else:
            return 'You should not do that'


class Apitoken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False, info={'label': 'Token'})
    secret = db.Column(db.String(255), unique=True, nullable=False, info={'label': 'Secret'})


user_datastore = SQLAlchemyUserDatastore(db, User, Role)


class Cat(db.Model):
    __tablename__ = "cat"

    id = db.Column(db.Integer, primary_key=True)
    radio = db.Column(db.String(250), nullable=False)
    frequency = db.Column(db.Integer(), nullable=False)
    mode = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=False), nullable=False)


class Config(db.Model):
    __tablename__ = "config"

    id = db.Column(db.Integer, primary_key=True)
    lotw_download_url = db.Column(db.String(255), default=None)
    lotw_upload_url = db.Column(db.String(255), default=None)
    lotw_rcvd_mark = db.Column(db.String(255), default=None)
    lotw_login_url = db.Column(db.String(255), default=None)
    eqsl_download_url = db.Column(db.String(255), default=None)
    eqsl_upload_url = db.Column(db.String(255), default=None)
    eqsl_rcvd_mark = db.Column(db.String(255), default=None)
    clublog_api_key = db.Column(db.String(255), default=None)


class ContestTemplate(db.Model):
    __tablename__ = "contest_template"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    band_160 = db.Column(db.String(20), nullable=False)
    band_80 = db.Column(db.String(20), nullable=False)
    band_40 = db.Column(db.String(20), nullable=False)
    band_20 = db.Column(db.String(20), nullable=False)
    band_15 = db.Column(db.String(20), nullable=False)
    band_10 = db.Column(db.String(20), nullable=False)
    band_6m = db.Column(db.String(20), nullable=False)
    band_4m = db.Column(db.String(20), nullable=False)
    band_2m = db.Column(db.String(20), nullable=False)
    band_70cm = db.Column(db.String(20), nullable=False)
    band_23cm = db.Column(db.String(20), nullable=False)
    mode_ssb = db.Column(db.String(20), nullable=False)
    mode_cw = db.Column(db.String(20), nullable=False)
    serial = db.Column(db.String(20), nullable=False)
    point_per_km = db.Column(db.String(20), nullable=False)
    qra = db.Column(db.String(20), nullable=False)
    other_exch = db.Column(db.String(255), nullable=False)
    scoring = db.Column(db.String(255), nullable=False)


class Contest(db.Model):
    __tablename__ = "contests"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    start = db.Column(db.DateTime(timezone=False), nullable=False)
    end = db.Column(db.DateTime(timezone=False), nullable=False)
    template = db.Column(db.Integer(), nullable=False)
    serial_num = db.Column(db.Integer(), nullable=False)
    # possible FK template->contest_template


class Contact(db.Model):
    __tablename__ = "contact"

    id = db.Column(db.Integer, primary_key=True)
    callsign = db.Column(db.String(32), nullable=False)
    gridsquare = db.Column(db.String(32))
    distance = db.Column(db.Float)
    bearing = db.Column(db.Float)
    bearing_star = db.Column(db.String(32))
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)


class Logbook(db.Model):
    __tablename__ = "logbook"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    callsign = db.Column(db.String(32), nullable=False)
    locator = db.Column(db.String(16), nullable=False)
    swl = db.Column(db.Boolean, default=False)
    default = db.Column(db.Boolean, default=False)
    public = db.Column(db.Boolean, default=True)
    eqsl_qth_nickname = db.Column(db.String(255))

    logs = db.relationship('Log', backref='logbook', lazy='dynamic')
    user_loggings = db.relationship('UserLogging', backref='logbook', lazy='dynamic')
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)


class Picture(db.Model):
    __tablename__ = "picture"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), unique=False, nullable=True)
    filesize = db.Column(db.Integer, unique=False, nullable=True, default=0)  # stored as bytes
    hash = db.Column(db.String(255), unique=True, nullable=True)

    log_id = db.Column(db.Integer(), db.ForeignKey('log.id'), nullable=False)


class Log(db.Model):
    __tablename__ = "log"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), default=None)
    age = db.Column(db.Integer, default=None)
    a_index = db.Column(db.Float, default=None)
    ant_az = db.Column(db.Float, default=None)
    ant_el = db.Column(db.Float, default=None)
    ant_path = db.Column(db.String(2), default=None)
    arrl_sect = db.Column(db.String(10), default=None)

    band_id = db.Column(db.Integer(), db.ForeignKey('bands.id'), nullable=False)

    band_rx = db.Column(db.String(10), default=None)
    biography = db.Column(db.Text)
    call = db.Column(db.String(32), default=None, index=True)
    check = db.Column(db.String(8), default=None)
    klass = db.Column(db.String(8), default=None)
    cnty = db.Column(db.String(32), default=None)
    comment = db.Column(db.UnicodeText())
    cont = db.Column(db.String(6), default=None, index=True)
    contacted_op = db.Column(db.String(32), default=None)
    contest_id = db.Column(db.String(32), default=None)
    country = db.Column(db.String(64), default=None)
    cqz = db.Column(db.Integer, default=None)
    distance = db.Column(db.Float, default=None)
    dxcc = db.Column(db.String(6), default=None, index=True)
    email = db.Column(db.String(255), default=None)
    eq_call = db.Column(db.String(32), default=None)
    eqsl_qslrdate = db.Column(db.DateTime(timezone=False), default=None)
    eqsl_qslsdate = db.Column(db.DateTime(timezone=False), default=None)
    eqsl_qsl_rcvd = db.Column(db.String(2), default=None)
    eqsl_qsl_sent = db.Column(db.String(2), default=None)
    eqsl_status = db.Column(db.String(255), default=None)
    force_init = db.Column(db.Integer, default=None)
    freq = db.Column(db.Integer, default=None)
    freq_rx = db.Column(db.Integer, default=None)
    gridsquare = db.Column(db.String(12), default=None)
    cache_gridsquare = db.Column(db.String(12), default=None)
    heading = db.Column(db.Float, default=None)
    iota = db.Column(db.String(10), default=None, index=True)
    ituz = db.Column(db.Integer, default=None)
    k_index = db.Column(db.Float, default=None)
    lat = db.Column(db.Float, default=None)
    lon = db.Column(db.Float, default=None)
    lotw_qslrdate = db.Column(db.DateTime(timezone=False), default=None)
    lotw_qslsdate = db.Column(db.DateTime(timezone=False), default=None)
    lotw_qsl_rcvd = db.Column(db.String(2), default=None)
    lotw_qsl_sent = db.Column(db.String(2), default=None)
    lotw_status = db.Column(db.String(255), default=None)
    max_bursts = db.Column(db.Integer, default=None)

    mode_id = db.Column(db.Integer(), db.ForeignKey('modes.id'), nullable=False)

    ms_shower = db.Column(db.String(32), default=None)
    my_city = db.Column(db.String(32), default=None)
    my_cnty = db.Column(db.String(32), default=None)
    my_country = db.Column(db.String(64), default=None)
    my_cq_zone = db.Column(db.Integer, default=None)
    my_gridsquare = db.Column(db.String(12), default=None)
    my_iota = db.Column(db.String(10), default=None)
    my_itu_zone = db.Column(db.String(11), default=None)
    my_lat = db.Column(db.Float, default=None)
    my_lon = db.Column(db.Float, default=None)
    my_name = db.Column(db.String(255), default=None)
    my_postal_code = db.Column(db.String(24), default=None)
    my_rig = db.Column(db.String(255), default=None)
    my_sig = db.Column(db.String(32), default=None)
    my_sig_info = db.Column(db.String(64), default=None)
    my_state = db.Column(db.String(32), default=None)
    my_street = db.Column(db.String(64), default=None)
    name = db.Column(db.String(128), default=None)
    notes = db.Column(db.Text, default=None)
    nr_bursts = db.Column(db.Integer, default=None)
    nr_pings = db.Column(db.Integer, default=None)
    operator = db.Column(db.String(32), default=None)
    owner_callsign = db.Column(db.String(32), default=None)
    pfx = db.Column(db.String(32), default=None, index=True)
    precedence = db.Column(db.String(32), default=None)
    prop_mode = db.Column(db.String(8), default=None)
    public_key = db.Column(db.String(255), default=None)
    qslmsg = db.Column(db.String(255), default=None)
    qslrdate = db.Column(db.DateTime(timezone=False), default=None)
    qslsdate = db.Column(db.DateTime(timezone=False), default=None)
    qsl_rcvd = db.Column(db.String(2), default=None)
    qsl_rcvd_via = db.Column(db.String(2), default=None)
    qsl_sent = db.Column(db.String(2), default=None)
    qsl_sent_via = db.Column(db.String(2), default=None)
    qsl_via = db.Column(db.String(64), default=None)
    qso_complete = db.Column(db.String(6), default=None)
    qso_random = db.Column(db.String(11), default=None)
    qth = db.Column(db.String(64), default=None)
    rig = db.Column(db.String(255), default=None)
    rst_rcvd = db.Column(db.String(32), default=None)
    rst_sent = db.Column(db.String(32), default=None)
    rx_pwr = db.Column(db.Float, default=None)
    sat_mode = db.Column(db.String(32), default=None, index=True)
    sat_name = db.Column(db.String(32), default=None, index=True)
    sfi = db.Column(db.Float, default=None)
    sig = db.Column(db.String(32), default=None)
    sig_info = db.Column(db.String(64), default=None)
    srx = db.Column(db.String(11), default=None)
    srx_string = db.Column(db.String(32), default=None)
    state = db.Column(db.String(32), default=None)
    station_callsign = db.Column(db.String(32), default=None)
    stx = db.Column(db.String(11), default=None)
    stx_info = db.Column(db.String(32), default=None)
    swl = db.Column(db.Integer, default=None)
    ten_ten = db.Column(db.Integer, default=None)
    time_off = db.Column(db.DateTime(timezone=False), default=None)
    time_on = db.Column(db.DateTime(timezone=False), default=None, index=True)
    tx_pwr = db.Column(db.Float, default=None)
    web = db.Column(db.String(255), default=None)
    user_defined_0 = db.Column(db.String(64), default=None)
    user_defined_1 = db.Column(db.String(64), default=None)
    user_defined_2 = db.Column(db.String(64), default=None)
    user_defined_3 = db.Column(db.String(64), default=None)
    user_defined_4 = db.Column(db.String(64), default=None)
    user_defined_5 = db.Column(db.String(64), default=None)
    user_defined_6 = db.Column(db.String(64), default=None)
    user_defined_7 = db.Column(db.String(64), default=None)
    user_defined_8 = db.Column(db.String(64), default=None)
    user_defined_9 = db.Column(db.String(64), default=None)
    credit_granted = db.Column(db.String(64), default=None)
    credit_submitted = db.Column(db.String(64), default=None)

    qsl_comment = db.Column(db.UnicodeText(), default=None)

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    logbook_id = db.Column(db.Integer(), db.ForeignKey('logbook.id'), nullable=False)
    pictures = db.relationship('Picture', backref='log', lazy='dynamic')
    user_loggings = db.relationship('UserLogging', backref='log', lazy='dynamic')

    __mapper_args__ = {"order_by": time_on.desc()}

    # Give a cute name <3 More like "name - callsign" or "callsign"
    def cutename(self):
        cutename(self.call, self.name)

    def country_grid_coords(self):
        return ham_country_grid_coords(self.call)

    def country_grid(self):
        q = ham_country_grid_coords(self.call)
        if q:
            return coords_to_qth(q['latitude'], q['longitude'], 6)['qth']
        else:
            return None

    def distance_from_user(self):
        if not self.gridsquare and not self.cache_gridsquare:
            qso_gs = self.country_grid()
        elif not self.gridsquare:
            qso_gs = self.cache_gridsquare
        else:
            qso_gs = self.gridsquare

        if not qso_gs or not self.user.locator:
            return None

        if not is_valid_qth(self.user.locator, 6) or not is_valid_qth(qso_gs, 6):
            return None

        _f = qth_to_coords(self.user.locator, 6)  # precision, latitude, longitude
        _t = qth_to_coords(qso_gs, 6)  # precision, latitude, longitude

        return distance.haversine_km(_f['latitude'],
                                     _f['longitude'],
                                     _t['latitude'],
                                     _t['longitude'])


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    cat = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    note = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=False), server_default=func.now(), onupdate=func.now())

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)

    __mapper_args__ = {"order_by": id.desc()}

    def timestamp_tz(self):
        t = self.timestamp
        if self.user.timezone.offset < 0:
            return t - datetime.timedelta(hours=self.user.timezone.offset)
        else:
            return t + datetime.timedelta(hours=self.user.timezone.offset)


class Mode(db.Model):
    __tablename__ = "modes"

    id = db.Column(db.Integer, primary_key=True)
    mode = db.Column(db.String(255), nullable=False)
    submode = db.Column(db.String(255), nullable=True)  # Unused as now

    logs = db.relationship('Log', backref='mode', lazy='dynamic')


class Band(db.Model):
    __tablename__ = "bands"

    id = db.Column(db.Integer, primary_key=True)
    modes = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    lower = db.Column(db.BigInteger(), nullable=True)
    upper = db.Column(db.BigInteger(), nullable=True)
    start = db.Column(db.BigInteger(), nullable=True)
    # Zone format 'iaru1', 'iaru2', 'iaru3'
    zone = db.Column(db.String(10), nullable=False, default='iaru1')

    logs = db.relationship('Log', backref='band', lazy='dynamic')


class DxccEntities(db.Model):
    __tablename__ = "dxcc_entities"

    id = db.Column(db.Integer, primary_key=True)
    adif = db.Column(db.Integer, nullable=False, index=True)
    name = db.Column(db.String(150), default=None)
    prefix = db.Column(db.String(30), nullable=False)
    cqz = db.Column(db.Float, nullable=False)
    ituz = db.Column(db.Float, nullable=False)
    cont = db.Column(db.String(5), nullable=False)
    long = db.Column(db.Float, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    start = db.Column(db.DateTime(timezone=False), default=None)
    end = db.Column(db.DateTime(timezone=False), default=None)


class DxccExceptions(db.Model):
    __tablename__ = "dxcc_exceptions"

    id = db.Column(db.Integer, primary_key=True)
    record = db.Column(db.Integer, nullable=False, index=True)
    call = db.Column(db.String(30), default=None)
    entity = db.Column(db.String(255), nullable=False)
    adif = db.Column(db.Integer, nullable=False)
    cqz = db.Column(db.Float, nullable=False)
    cont = db.Column(db.String(5), default=None)
    long = db.Column(db.Float, default=None)
    lat = db.Column(db.Float, default=None)
    start = db.Column(db.DateTime(timezone=False), default=None)
    end = db.Column(db.DateTime(timezone=False), default=None)


class DxccPrefixes(db.Model):
    __tablename__ = "dxcc_prefixes"

    id = db.Column(db.Integer, primary_key=True)
    record = db.Column(db.Integer, nullable=False, index=True)
    call = db.Column(db.String(30), default=None)
    entity = db.Column(db.String(255), nullable=False)
    adif = db.Column(db.Integer, nullable=False)
    cqz = db.Column(db.Float, nullable=False)
    cont = db.Column(db.String(5), default=None)
    long = db.Column(db.Float, default=None)
    lat = db.Column(db.Float, default=None)
    start = db.Column(db.DateTime(timezone=False), default=None)
    end = db.Column(db.DateTime(timezone=False), default=None)


class Logging(db.Model):
    __tablename__ = "logging"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255), nullable=False, default="General")
    level = db.Column(db.String(255), nullable=False, default="INFO")
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=False), server_default=func.now(), onupdate=func.now())

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=True)


class UserLogging(db.Model):
    __tablename__ = "user_logging"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255), nullable=False, default="General")
    level = db.Column(db.String(255), nullable=False, default="INFO")
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=False), server_default=func.now(), onupdate=func.now())

    log_id = db.Column(db.Integer(), db.ForeignKey('log.id'), nullable=True)
    logbook_id = db.Column(db.Integer(), db.ForeignKey('logbook.id'), nullable=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)


# Utils functions
def ham_country_grid_coords(call):
    if 'sqlite' in db.engine.driver:
        q = DxccPrefixes.query.filter(
            DxccPrefixes.call == func.substr(call, 1, func.LENGTH(DxccPrefixes.call))
        ).order_by(func.length(DxccPrefixes.call).desc()).limit(1)
    else:
        q = DxccPrefixes.query.filter(
            DxccPrefixes.call == func.substring(call, 1, func.LENGTH(DxccPrefixes.call))
        ).order_by(func.length(DxccPrefixes.call).desc()).limit(1)
    if q.count() <= 0:
        return None
    else:
        qth = coords_to_qth(q[0].lat, q[0].long, 6)
        return {'qth': qth['qth'], 'latitude': q[0].lat, 'longitude': q[0].long}


# Give a cute name <3 More like "name - callsign" or "callsign"
def cutename(call, name=None):
    cute = ""
    if name:
        cute += name
        cute += " - "
    cute += call
    return cute
