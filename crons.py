from __future__ import print_function

import gzip
import os
import shutil
import urllib.parse
import urllib.error
import urllib.request
import xml.etree.ElementTree as ElementTree
import re
import datetime

from dateutil import parser
from flask import current_app

from libjambon import eqsl_upload_log, get_dxcc_from_clublog_or_database
from models import db, DxccEntities, DxccExceptions, DxccPrefixes, Log, Config, UserLogging, User, Logbook
from utils import add_log
from adif import parse as parse_adif

from pyhamqth import HamQTH, HamQTHQueryFailed


def update_qsos_from_hamqth():
    users = User.query.filter(User.hamqth_name.isnot(None), User.hamqth_password.isnot(None)).all()
    for user in users:
        updated = 0

        logs = Log.query.filter(Log.consolidated_hamqth.is_(False), Log.user_id == user.id).all()
        _v = "AHRL"
        _hq = HamQTH(user=user.hamqth_name, password=user.hamqth_password, user_agent_suffix=_v)

        for log in logs:
            if not log.call:
                pass
            try:
                _csd = _hq.lookup_callsign_data(log.call)
            except HamQTHQueryFailed as e:
                print("Failed for {0}: {1}".format(log.call, e))
                err = UserLogging()
                err.user_id = log.user.id
                err.log_id = log.id
                err.logbook_id = log.logbook.id
                err.category = "HamQTH"
                err.level = "ERROR"
                err.message = "Query failed or call not found: {0}".format(e)
                db.session.add(err)
                log.consolidated_hamqth = True
                continue

            if "nick" in _csd and not log.name:
                log.name = _csd["nick"]
            if "qth" in _csd and not log.qth:
                log.qth = _csd["qth"]
            if "grid" in _csd and not log.gridsquare:
                log.gridsquare = _csd["grid"]
            # if 'country' in _csd and not log.country:
            #    log.country = _csd['country']
            # We must leave country filled by DXCC Clublog or Database I think finally
            if "latitude" in _csd and not log.lat:
                log.lat = _csd["latitude"]
            if "longitude" in _csd and not log.lon:
                log.lon = _csd["longitude"]
            if "web" in _csd and not log.web:
                log.web = _csd["web"]
            if "iota" in _csd and not log.iota:
                log.iota = _csd["iota"]

            log.consolidated_hamqth = True
            updated += 1

        db.session.commit()

        print("Updated {0} QSOs for {1}".format(updated, user.name))


def update_qsos_without_countries():
    updated = 0
    logs = Log.query.filter(Log.country.is_(None) | Log.dxcc.is_(None) | Log.cqz.is_(None)).all()
    for log in logs:
        if not log.call:
            continue
        dxcc = get_dxcc_from_clublog_or_database(log.call)
        log.dxcc = dxcc["DXCC"]
        log.cqz = dxcc["CQZ"]
        log.country = dxcc["Name"]
        log.cont = dxcc["Continent"]
        db.session.commit()
        updated += 1
    print("Updated {0} QSOs".format(updated))


def populate_logs_gridsquare_cache():
    updated = 0
    logs = Log.query.filter(Log.cache_gridsquare.is_(None)).all()
    for log in logs:
        qth = log.country_grid_coords()
        if not qth:
            print("!! country_grid_coords() for log {0} returned None, please check !!".format(log.id))
            continue
        log.cache_gridsquare = qth["qth"]
        updated += 1
    db.session.commit()
    print("-- Updated {0} QSOs".format(updated))


def update_dxcc_from_cty_xml(_file=None, silent=False):
    if not silent:
        print("--- Updating DXCC tables (prefixes, entities, exceptions) from cty.xml")
    fname = os.path.join(current_app.config["TEMP_DOWNLOAD_FOLDER"], "cty.xml")

    config = Config.query.first()
    if not config:
        if not silent:
            print("!!! Error: config not found")
        add_log(category="CONFIG", level="ERROR", message="Config not found")
        return

    if os.path.isfile(fname):
        os.remove(fname)
        if not silent:
            print("-- Removed old file {0}".format(fname))

    if not _file:
        if not silent:
            print("-- Downloading...")
        if not config.clublog_api_key:
            if not silent:
                print("!! Clublog API Key not defined")
            add_log(category="CRONS", level="ERROR", message="Clublog API Key not defined")
            return
        url = "https://secure.clublog.org/cty.php?api={0}".format(config.clublog_api_key)

        try:
            with urllib.request.urlopen(url) as response, open(fname, "wb") as out_file:
                with gzip.GzipFile(fileobj=response) as uncompressed:
                    shutil.copyfileobj(uncompressed, out_file)
        except urllib.error.URLError as err:
            if not silent:
                print("!! Error: {0}".format(err))
            exit(-1)
        if not silent:
            print("-- File downloaded at {0}".format(fname))
    elif os.path.isfile(_file):
        fname = _file
        if not silent:
            print("-- File at {0}".format(fname))
    else:
        if not silent:
            print("-- derp ?")
        exit()

    # Now parse XML file
    tree = None
    try:
        tree = ElementTree.parse(fname)
    except FileNotFoundError as err:
        if not silent:
            print("!! Error: {0}".format(err))
        exit(-1)
    except ElementTree.ParseError as err:
        if not silent:
            print("!! Error: {0}".format(err))
        exit(-1)

    if not tree:
        exit(-1)

    root = tree.getroot()

    for element in root:
        if element.tag == "{http://www.clublog.org/cty/v1.0}entities":
            if not silent:
                print("++ Parsing {0}".format(element.tag))
            rmed = DxccEntities.query.delete()
            if not silent:
                print("-- Cleaned {0} old entries".format(rmed))
            parse_element(element, silent)

        elif element.tag == "{http://www.clublog.org/cty/v1.0}exceptions":
            if not silent:
                print("++ Parsing {0}".format(element.tag))
            rmed = DxccExceptions.query.delete()
            if not silent:
                print("-- Cleaned {0} old entries".format(rmed))
            parse_element(element, silent)

        elif element.tag == "{http://www.clublog.org/cty/v1.0}prefixes":
            if not silent:
                print("++ Parsing {0}".format(element.tag))
            rmed = DxccPrefixes.query.delete()
            if not silent:
                print("-- Cleaned {0} old entries".format(rmed))
            parse_element(element, silent)


def parse_element(element, silent=False):
    elements = 0
    for child in element:
        skip = False

        if element.tag == "{http://www.clublog.org/cty/v1.0}entities":
            _obj = DxccEntities()
            _obj.ituz = 999  # We don't have ITUZ in cty.xml so we put 999 in it
        elif element.tag == "{http://www.clublog.org/cty/v1.0}exceptions":
            _obj = DxccExceptions()
        elif element.tag == "{http://www.clublog.org/cty/v1.0}prefixes":
            _obj = DxccPrefixes()
        else:
            return

        if "record" in child.attrib:
            _obj.record = child.attrib["record"]

        for attr in child:
            if attr.tag == "{http://www.clublog.org/cty/v1.0}call":
                _obj.call = attr.text
            elif attr.tag == "{http://www.clublog.org/cty/v1.0}name":
                _obj.name = attr.text
            elif attr.tag == "{http://www.clublog.org/cty/v1.0}prefix":
                _obj.prefix = attr.text
            elif attr.tag == "{http://www.clublog.org/cty/v1.0}entity":
                if attr.text == "INVALID":
                    skip = True
                _obj.entity = attr.text
            elif attr.tag == "{http://www.clublog.org/cty/v1.0}adif":
                _obj.adif = int(attr.text)
            elif attr.tag == "{http://www.clublog.org/cty/v1.0}cqz":
                _obj.cqz = float(attr.text)
            elif attr.tag == "{http://www.clublog.org/cty/v1.0}cont":
                _obj.cont = attr.text
            elif attr.tag == "{http://www.clublog.org/cty/v1.0}long":
                _obj.long = float(attr.text)
            elif attr.tag == "{http://www.clublog.org/cty/v1.0}lat":
                _obj.lat = float(attr.text)
            elif attr.tag == "{http://www.clublog.org/cty/v1.0}start":
                _obj.start = parser.parse(attr.text)
            elif attr.tag == "{http://www.clublog.org/cty/v1.0}end":
                _obj.start = parser.parse(attr.text)

            if not _obj.adif:
                _obj.adif = 999
            elif not _obj.cqz:
                _obj.cqz = 999

        if skip:
            continue  # We have god an entity=INVALID, skip it

        db.session.add(_obj)
        elements += 1
    db.session.commit()
    if not silent:
        print("-- Committed {0} new elements".format(elements))


def cron_sync_from_eqsl(dry_run=False):
    """ https://www.eqsl.cc/qslcard/DownloadInBox.txt """

    """
    todo: to avoid downloading too much (not really in fact) logs, get the oldest time with a eqsl_rcvd == 'N'
    and put it in query with RcvdSince = (YYYYMMDDHHMM)
    """

    if dry_run:
        print("-- [DRY RUN] Fetching logs from eQSL")
    else:
        print("-- Fetching logs from eQSL")

    _logbooks = Logbook.query.filter(Logbook.eqsl_qth_nickname.isnot(None)).all()
    for logbook in _logbooks:
        if not logbook.user.eqsl_name or not logbook.user.eqsl_password:
            continue  # Skip logbooks of user not using eQSL

        config = Config.query.first()
        if not config:
            print("!!! Error: config not found")
            add_log(category="CONFIG", level="ERROR", message="Config not found")
            return

        print("-- Working on logbook [{0}] {1}".format(logbook.id, logbook.name))

        _payload = urllib.parse.urlencode(
            {
                "UserName": logbook.user.eqsl_name,
                "Password": logbook.user.eqsl_password,
                "QTHNickname": logbook.eqsl_qth_nickname,
            }
        )

        _url = "{0}?{1}".format(config.eqsl_download_url, _payload)

        _req = urllib.request.Request(_url)
        _text = None

        err_fetch = UserLogging()
        err_fetch.user_id = logbook.user.id
        err_fetch.logbook_id = logbook.id
        err_fetch.category = "EQSL FETCH"

        try:
            with urllib.request.urlopen(_req) as f:
                _text = f.read().decode("UTF-8")
        except urllib.error.URLError as e:
            err_fetch.level = "ERROR"
            err_fetch.message = "Error fetching from eQSL: {0}".format(e)
            db.session.add(err_fetch)
            db.session.commit()
            continue  # skip to next

        if not _text:
            err_fetch.level = "ERROR"
            err_fetch.message = "Error fetching from EQSL, _text undefined"
            db.session.add(err_fetch)
            db.session.commit()
            continue  # skip to next

        # Now get the download link
        # <li><a href="downloadedfiles/xxx.adi">.ADI file</a>
        m = re.search('<A HREF="(.*)">.ADI file</A>', _text)

        if m:
            _file_path = m.group(1)
            _url = "{0}/{1}".format(os.path.dirname(config.eqsl_download_url), _file_path)
            _req = urllib.request.Request(_url)
            _text = None

            try:
                print("-- Fetching ADIF {0}".format(_url))
                with urllib.request.urlopen(_req) as f:
                    # eQSL returns a file encoded in ISO8859-1 so decode it then re-encode it in UTF-8
                    _text = f.read().decode("ISO8859-1").encode("UTF-8")
            except urllib.error.URLError as e:
                err_fetch.level = "ERROR"
                err_fetch.message = "Error fetching from eQSL: {0}".format(e)
                db.session.add(err_fetch)
                db.session.commit()
                continue  # skip to next

            if not _text:
                err_fetch.level = "ERROR"
                err_fetch.message = "Error fetching from EQSL, _text for final URL undefined"
                db.session.add(err_fetch)
                db.session.commit()
                continue  # skip to next

            adif = parse_adif(_text)

            for log in adif:
                err_log = UserLogging()
                err_log.user_id = logbook.user.id
                err_log.logbook_id = logbook.id
                err_log.category = "EQSL LOG"

                _date = "{0} {1}".format(log["qso_date"], log["time_on"])
                _date_first = datetime.datetime.strptime(_date + "00", "%Y%m%d %H%M%S")
                _date_second = datetime.datetime.strptime(_date + "59", "%Y%m%d %H%M%S")
                # Try to find a matching log entry
                qso = Log.query.filter(
                    Log.logbook_id == logbook.id,
                    Log.user_id == logbook.user.id,
                    Log.call == log["call"].upper(),
                    Log.time_on.between(_date_first, _date_second),
                ).first()
                if qso:
                    if qso.eqsl_qsl_rcvd == "Y":
                        continue  # this eQSL have already been matched
                    print("-- Matching log found for {0} on {1} : ID {2}".format(log["call"], _date, qso.id))
                    if not dry_run:
                        qso.eqsl_qsl_rcvd = "Y"
                        err_log.log_id = qso.id
                        err_log.level = "INFO"
                        err_log.message = "QSO from eQSL by {0} on {1} received and updated".format(log["call"], _date)
                else:
                    print("-- No matching log found for {0} on {1}".format(log["call"], _date))
                    err_log.level = "INFO"
                    err_log.message = "QSO from eQSL by {0} on {1} not found in database".format(log["call"], _date)
                if not dry_run:
                    db.session.add(err_log)
                    db.session.commit()
        else:
            err_fetch.level = "ERROR"
            err_fetch.message = "Error fetching from EQSL, link not found in body"
            db.session.add(err_fetch)
            db.session.commit()


def cron_sync_eqsl(dry_run=False):
    """ https://www.eqsl.cc/qslcard/ImportADIF.txt """

    if dry_run:
        print("--- [DRY RUN] Sending logs to eQSL when requested")
    else:
        print("--- Sending logs to eQSL when requested")
    logs = Log.query.filter(Log.eqsl_qsl_sent == "R").all()
    config = Config.query.first()
    if not config:
        print("!!! Error: config not found")
        add_log(category="CONFIG", level="ERROR", message="Config not found")
        return

    for log in logs:
        status = eqsl_upload_log(log, config, dry_run)
        if dry_run:
            continue
        err = UserLogging()
        err.user_id = log.user.id
        err.log_id = log.id
        err.logbook_id = log.logbook.id
        err.category = "EQSL"

        if status["state"] == "error":
            err.level = "ERROR"
            print("!! Error uploading QSO {0} to eQSL: {1}".format(log.id, status["message"]))
        elif status["state"] == "rejected":
            log.eqsl_qsl_sent = "I"
            print("!! Rejected uploading QSO {0} to eQSL: {1}".format(log.id, status["message"]))
        else:
            err.level = "INFO"

        err.message = status["message"] + "\r\n"

        if "msgs" in status:
            for i in status["msgs"]:
                print("!! {0}: {1}".format(i[0], i[1]))
                err.message += "{0}: {1}\r\n".format(i[0], i[1])

        if status["state"] == "success":
            log.eqsl_qsl_sent = "Y"

        print(status)

        db.session.add(err)
        db.session.commit()
