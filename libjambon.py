import math
import re
import urllib.request
import urllib.parse
import urllib.error

import bs4 as beautiful_soup
import requests
from flask import json
from sqlalchemy import or_, func

from models import Band, Mode, Config, DxccPrefixes
from utils import add_log, InvalidUsage


def band_to_frequency(band, mode):
    if not isinstance(band, int) or not isinstance(mode, int):
        raise TypeError("Sorry but only integer")

    b = Band.query.filter(Band.id == band).first()
    m = Mode.query.filter(Mode.id == mode).first()

    if not b or not m:
        return None

    frequencies = Band.query.filter(
        Band.lower.is_(None),
        Band.upper.is_(None),
        Band.name == b.name,
        or_(Band.modes.contains(m.submode), Band.modes.contains(m.mode)),
    )

    if frequencies.count() <= 0:
        return b.lower
    else:
        return frequencies.first().start


def frequency_to_band(frequency, zone="iaru1"):
    f = frequency
    if type(f) == str:
        f = int(frequency)

    f_q = Band.query.filter(Band.start.is_(None), Band.lower < f, Band.upper > f, Band.zone == zone).single()
    return f_q.name


def geo_bearing_star(bearing):
    dirs = ["N", "E", "S", "W"]

    rounded = round(bearing / 22.5) % 16
    if (rounded % 4) == 0:
        _dir = dirs[int(rounded / 4)]
    else:
        _dir = dirs[int(2 * math.floor(((math.floor(rounded / 4) + 1) % 4) / 2))]
        _dir += dirs[int(1 + 2 * math.floor(rounded / 8))]
    return _dir


def adif(k, v):
    v = str(v)
    return "<{0}:{1}>{2} ".format(k.upper(), len(v), v)


def eqsl_upload_log(log, config, dry_run):
    """ Doc: https://www.eqsl.cc/qslcard/ImportADIF.txt """
    reject = False
    # Sanity check
    if not config.eqsl_download_url:
        return {"state": "error", "message": "config.eqsl_download_url empty"}
    if not log.user.eqsl_name:
        return {"state": "error", "message": "user.eqsl_name empty"}
    if not log.user.eqsl_password:
        return {"state": "error", "message": "user.eqsl_password empty"}
    if not log.call:
        return {"state": "error", "message": "log.call empty"}
    if not log.band:
        return {"state": "error", "message": "log.band empty"}
    if not log.mode:
        return {"state": "error", "message": "log.mode empty"}
    if not log.time_on:
        return {"state": "error", "message": "log.time_on empty"}
    if not log.rst_sent:
        return {"state": "error", "message": "log.rst_sent empty"}
    if not log.logbook.eqsl_qth_nickname:
        return {"state": "error", "message": "log.logbook.eqsl_qth_nickname empty"}
    # End of checks
    # Build URL
    url = config.eqsl_upload_url
    log_adif = "AHRL Upload"
    log_adif += adif("adif_ver", "1.00") + " \r\n"
    # Test
    # log_adif += adif('eqsl_user', 'TEST-SWL') + ' '
    # log_adif += adif('eqsl_pswd', 'Testpswd') + ' '
    # Real ones
    log_adif += adif("eqsl_user", log.user.eqsl_name) + " "
    log_adif += adif("eqsl_pswd", log.user.eqsl_password) + " "
    log_adif += "<EOH> "
    log_adif += adif("band", log.band.name.upper()) + " \r\n"
    # Test
    # log_adif += adif('call', 'TEST-SWL') + ' '
    # Real one
    log_adif += adif("call", log.call.upper()) + " "

    # eQSL Mode standardization (http://www.eqsl.cc/qslcard/ADIFContentSpecs.cfm)
    mode = log.mode.submode
    if log.mode.mode == "OLIVIA":
        mode = "OLIVIA"
    elif log.mode.submode == "PAC4":
        mode = "PAC"
    elif log.mode.submode in ["PSK250", "PSK500", "PSK1000", "QPSK250", "QPSK500", "PSK2K", "FSKHELL"]:
        reject = True
    elif log.mode.mode == "JT9":
        mode = "JT9"
    elif log.mode.mode == "JT65":
        mode = "JT65"
    elif log.mode.mode == "ISCAT":
        mode = "ISCAT"
    elif log.mode.submode == "USB" or log.mode.submode == "LSB":
        mode = "SSB"
    elif log.mode.mode == "ROS":
        mode = "ROS"
    elif log.mode.submode == "DOMINOEX":
        mode = "DOMINO"
    elif log.mode.mode == "OPERA":
        mode = "OPERA"
    elif log.mode.submode in ["MFSK4", "MFSK11", "MFSK22", "MFSK31", "MFSK32", "MFSK64", "MFSK128"]:
        reject = True

    if reject:
        # Theses are modes not managed by eQSL, sorry
        return {
            "state": "rejected",
            "message": "rejected because mode {0} not managed by eQSL".format(log.mode.submode),
        }

    log_adif += adif("mode", mode.upper()) + " "

    log_adif += adif("qso_date", log.time_on.strftime("%Y%m%d")) + " "
    log_adif += adif("rst_sent", log.rst_sent) + " "
    log_adif += adif("time_on", log.time_on.strftime("%H%M%S")) + " \r\n"
    log_adif += adif("APP_EQSL_QTH_NICKNAME", log.logbook.eqsl_qth_nickname) + " "
    if log.qsl_comment:
        log_adif += adif("qslmsg", log.qsl_comment) + " "
    log_adif += "<EOR>"

    if dry_run:
        print("--- [DRY RUN] what would be commited for {0}:".format(log.id))
        print(log_adif)
        return

    try:
        data = urllib.parse.urlencode({"ADIFData": log_adif})
        data = data.encode("utf-8")
        req = urllib.request.Request(url, data)
        resp = urllib.request.urlopen(req)
    except ValueError as e:
        return {"state": "error", "message": str(e)}
    except urllib.error.URLError as e:
        return {"state": "error", "message": str(e)}

    soup = beautiful_soup.BeautifulSoup(resp.read(), "html.parser")

    body = soup.body.get_text().strip()

    # print(body)

    # Possible: 'Result', 'Warning', 'Error'
    rejected = False
    results = []
    for result in body.split("\r\n"):
        if result.strip() == "" or not result.strip():
            continue  # Ignore empty lines
        obj = re.match(r"^(\w+): (.+)", result.strip())
        results.append([obj.group(1), obj.group(2)])
        if obj.group(2) == "0 out of 1 records added" or obj.group(1) == "Error":
            rejected = True

    if not rejected:
        return {"state": "success", "message": "QSO Sync-ed to eQSL", "msgs": results}
    else:
        return {"state": "error", "message": "Some errors where detected", "msgs": results}


# To be managed a-part: band, klass (class), freq, freq_rx, mode, time_on, qso_date, comment
ADIF_FIELDS = [
    "address",
    "age",
    "a_index",
    "ant_az",
    "ant_el",
    "ant_path",
    "arrl_sect",
    "biography",
    "band_rx",
    "call",
    "check",
    "cnty",
    "cont",
    "contacted_op",
    "contest_id",
    "country",
    "cqz",
    "distance",
    "dxcc",
    "email",
    "eq_call",
    "eqsl_qslrdate",
    "eqsl_qslsdate",
    "eqsl_qsl_rcvd",
    "eqsl_qsl_sent",
    "eqsl_status",
    "force_init",
    "gridsquare",
    "heading",
    "iota",
    "ituz",
    "k_index",
    "lat",
    "lon",
    "lotw_qslrdate",
    "lotw_qslsdate",
    "lotw_qsl_rcvd",
    "lotw_qsl_sent",
    "lotw_status",
    "max_bursts",
    "ms_shower",
    "my_city",
    "my_cnty",
    "my_country",
    "my_cq_zone",
    "my_gridsquare",
    "my_iota",
    "my_itu_zone",
    "my_lat",
    "my_lon",
    "my_name",
    "my_postal_code",
    "my_rig",
    "my_sig",
    "my_sig_info",
    "my_state",
    "my_street",
    "name",
    "notes",
    "nr_bursts",
    "nr_pings",
    "operator",
    "owner_callsign",
    "pfx",
    "precedence",
    "prop_mode",
    "public_key",
    "qslmsg",
    "qslrdate",
    "qslsdate",
    "qsl_rcvd",
    "qsl_rcvd_via",
    "qsl_sent",
    "qsl_sent_via",
    "qsl_via",
    "qso_complete",
    "qso_random",
    "qth",
    "rig",
    "rst_rcvd",
    "rst_sent",
    "rx_pwr",
    "sat_mode",
    "sat_name",
    "sfi",
    "sig",
    "sig_info",
    "srx",
    "srx_string",
    "state",
    "station_callsign",
    "stx",
    "stx_info",
    "swl",
    "ten_ten",
    "tx_pwr",
    "web",
    "credit_granted",
    "credit_submitted",
]


def get_dxcc_from_clublog(callsign):
    config = Config.query.first()
    if not config:
        print("!!! Error: config not found")
        add_log(category="CONFIG", level="ERROR", message="Config not found")
        return

    clublog_api_key = config.clublog_api_key
    clublog_uri = "https://secure.clublog.org/dxcc?call={0}&api={1}&full=1".format(callsign, clublog_api_key)

    try:
        r = requests.get(clublog_uri)
    except:  # noqa: E722
        raise InvalidUsage("Error getting DXCC from ClubLog", status_code=500)

    if r.status_code != 200:
        raise InvalidUsage("Error getting DXCC from ClubLog", status_code=r.status_code)

    return json.loads(r.content)


def get_dxcc_from_clublog_or_database(callsign):
    response = {}
    dxcc_database = None
    dxcc_clublog = get_dxcc_from_clublog(callsign)

    if not dxcc_clublog:
        # Trying fallback from database
        q = (
            DxccPrefixes.query.filter(DxccPrefixes.call == func.substring(callsign, 1, func.LENGTH(DxccPrefixes.call)))
            .order_by(func.length(DxccPrefixes.call).asc())
            .limit(1)
            .first()
        )
        if q:
            dxcc_database = {
                "CQZ": int(q.cqz),
                "Continent": q.cont,
                "DXCC": q.adif,
                "Lat": q.lat,
                "Lon": q.long,
                "Name": q.entity,
                "PermKomi": False,
            }

    if not dxcc_clublog and not dxcc_database:
        # We have nothing at all :(
        raise InvalidUsage("Error while getting infos from clublog", status_code=500)

    if dxcc_clublog or dxcc_database:
        response["status"] = "ok"
        if dxcc_clublog:
            response.update(dxcc_clublog)
            response["source"] = "clublog"
        else:
            response.update(dxcc_database)
            response["source"] = "database"

    return response


def coordinates2adif(coord, _type):
    """
    a sequence of characters representing a latitude or longitude in XDDD MM.MMM format, where

    X is a directional Character from the set {E, W, N, S}
    DDD is a 3-Digit degrees specifier, where 0 <= DDD <= 180 [use leading zeroes]
    MM.MMM is a 6-Digit minutes specifier, where 0 <= MM.MMM <= 59.999  [use leading zeroes]
    """
    degrees = int(coord)
    minutes = abs((coord - int(coord)) * 60)

    direction = ""
    if _type == "Longitude":
        if degrees <= 0:
            direction = "W"
            degrees = abs(degrees)
        elif degrees > 0:
            direction = "E"
        else:
            direction = ""
    elif _type == "Latitude":
        if degrees < 0:
            direction = "S"
            degrees = abs(degrees)
        elif degrees > 0:
            direction = "N"
        else:
            direction = ""

    return "{0}{1} {min:06.3f}".format(direction, str(degrees).zfill(3), min=minutes)


def adif2coordinates(coord):
    """
    a sequence of characters representing a latitude or longitude in XDDD MM.MMM format, where

    X is a directional Character from the set {E, W, N, S}
    DDD is a 3-Digit degrees specifier, where 0 <= DDD <= 180 [use leading zeroes]
    MM.MMM is a 6-Digit minutes specifier, where 0 <= MM.MMM <= 59.999  [use leading zeroes]
    """
    p = re.match(r"([NWES])([\d]{3})\s(\d\d\.\d\d\d)", coord)

    coords = int(p.group(2)) + float(p.group(3)) / 60.0
    if p.group(1) in ["W", "S"] and coords >= 0:
        coords = math.fabs(coords) * -1

    return coords
