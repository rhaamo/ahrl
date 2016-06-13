import re
from unidecode import unidecode
from models import db, Apitoken, Band
import random
import string
import os
from flask_security import current_user
import pytz
from flask import flash, current_app, json
from markupsafe import Markup
from functools import wraps
import requests

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

# To be managed a-part: band, klass (class), freq, freq_rx, mode, time_on, qso_date, comment
ADIF_FIELDS = ['address', 'age', 'a_index', 'ant_az', 'ant_el', 'ant_path', 'arrl_sect', 'biography',
               'band_rx', 'call', 'check', 'cnty', 'cont', 'contacted_op', 'contest_id',
               'country', 'cqz', 'distance', 'dxcc', 'email', 'eq_call', 'eqsl_qslrdate',
               'eqsl_qslsdate', 'eqsl_qsl_rcvd', 'eqsl_qsl_sent', 'eqsl_status', 'force_init',
               'gridsquare', 'heading', 'iota', 'ituz', 'k_index', 'lat', 'lon',
               'lotw_qslrdate', 'lotw_qslsdate', 'lotw_qsl_rcvd', 'lotw_qsl_sent', 'lotw_status',
               'max_bursts', 'ms_shower', 'my_city', 'my_cnty', 'my_country', 'my_cq_zone',
               'my_gridsquare', 'my_iota', 'my_itu_zone', 'my_lat', 'my_lon', 'my_name',
               'my_postal_code', 'my_rig', 'my_sig', 'my_sig_info', 'my_state', 'my_street',
               'name', 'notes', 'nr_bursts', 'nr_pings', 'operator', 'owner_callsign', 'pfx',
               'precedence', 'prop_mode', 'public_key', 'qslmsg', 'qslrdate', 'qslsdate',
               'qsl_rcvd', 'qsl_rcvd_via', 'qsl_sent', 'qsl_sent_via', 'qsl_via', 'qso_complete',
               'qso_random', 'qth', 'rig', 'rst_rcvd', 'rst_sent', 'rx_pwr', 'sat_mode', 'sat_name',
               'sfi', 'sig', 'sig_info', 'srx', 'srx_string', 'state', 'station_callsign', 'stx',
               'stx_info', 'swl', 'ten_ten', 'time_off', 'tx_pwr', 'web', 'credit_granted',
               'credit_submitted']


def slugify(text, delim=u'_'):
    """
    Generate a slug in ASCII-only form
    :param text: Text to slugify
    :param delim: Delimiter to join
    :return: str slug
    """
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return delim.join(result)


def gen_random_str(size=10):
    """
    Generate random string
    :param size: Size of string
    :return: Random string
    """
    return ''.join(random.choice(string.ascii_uppercase +
                                 string.ascii_lowercase +
                                 string.digits) for _ in range(size))


def path_or_none(fbase, ftype, fname):
    """
    Return path or none
    :param fbase: Base directory
    :param ftype: Type directory
    :param fname: Filename
    :return: Full path or None
    """
    if not fbase or not ftype or not fname:
        return None
    fpath = os.path.join(fbase, ftype, fname)
    return fpath if os.path.isfile(fpath) else None


def generate_uniques_apitoken():
    """
    Generate an unique API Token
    :return: Dict of token and secret pair
    """
    while 1:
        tmp_token = gen_random_str(20)
        tmp_secret = gen_random_str(20)

        blip = Apitoken.query.filter_by(token=tmp_token,
                                        secret=tmp_secret).first()
        if blip:
            continue
        else:
            return {"token": tmp_token, "secret": tmp_secret}

    return None


def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def dt_utc_to_user_tz(dt, user=None):
    if not user:
        user = current_user
    user_tz = pytz.timezone(user.timezone)
    if dt.tzinfo == user_tz:
        return dt  # already converted
    utc_dt = pytz.timezone('UTC').localize(dt)  # Makes a naive-UTC DateTime
    return utc_dt.astimezone(user_tz)           # Then convert it to the user_tz


def show_date_no_offset(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S')


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        rv['code'] = self.status_code
        return rv


def check_default_profile(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        errs = []
        if current_user.is_authenticated:
            if current_user.callsign == 'N0C4LL':
                errs.append("Profile callsign not changed !")
            if current_user.locator == 'JN':
                errs.append("Profile locator not changed !")

            bands = db.session.query(Band.id).filter(Band.modes.is_(None),
                                                     Band.start.is_(None),
                                                     Band.zone == current_user.zone).count()
            if bands <= 0 or not bands:
                errs.append("The IARU Zone you selected doesn't have any band defined in AHRL yet. See with devs please.")

        if len(errs) > 0:
            flash(Markup("Errors:<br />{0}".format("<br />".join(errs))), 'error')
        return f(*args, **kwargs)
    return wrap


def get_dxcc_from_clublog(callsign):
    clublog_api_key = current_app.config['CLUBLOG_API_KEY']
    clublog_uri = "https://secure.clublog.org/dxcc?call={0}&api={1}&full=1".format(callsign, clublog_api_key)

    try:
        r = requests.get(clublog_uri)
    except:
        raise InvalidUsage('Error getting DXCC from ClubLog', status_code=500)

    if r.status_code != 200:
        raise InvalidUsage('Error getting DXCC from ClubLog', status_code=r.status_code)

    return json.loads(r.content)
