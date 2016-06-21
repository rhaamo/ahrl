from __future__ import print_function
from utils import get_dxcc_from_clublog, add_log
import urllib.request
import shutil
import os
import gzip
from flask import current_app
import xml.etree.ElementTree as ElementTree
from models import db, DxccEntities, DxccExceptions, DxccPrefixes, Log, Config, UserLogging, Logging
from dateutil import parser
from libjambon import eqsl_upload_log


def update_qsos_without_countries():
    updated = 0
    logs = Log.query.filter(Log.country.is_(None) | Log.dxcc.is_(None) | Log.cqz.is_(None)).all()
    for log in logs:
        if not log.call:
            continue
        dxcc = get_dxcc_from_clublog(log.call)
        log.dxcc = dxcc['DXCC']
        log.cqz = dxcc['CQZ']
        log.country = dxcc['Name']
        log.cont = dxcc['Continent']
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
        log.cache_gridsquare = qth['qth']
        updated += 1
    db.session.commit()
    print("-- Updated {0} QSOs".format(updated))


def update_dxcc_from_cty_xml():
    print("--- Updating DXCC tables (prefixes, entities, exceptions) from cty.xml")
    fname = os.path.join(current_app.config['TEMP_DOWNLOAD_FOLDER'], 'cty.xml')

    config = Config.query.first()
    if not config:
        print("!!! Error: config not found")
        add_log(category='CONFIG', level='ERROR', message='Config not found')
        return

    if os.path.isfile(fname):
        os.remove(fname)
        print("-- Removed old file {0}".format(fname))

    print("-- Downloading...")
    if not config.clublog_api_key:
        print("!! Clublog API Key not defined")
        add_log(category='CRONS', level='ERROR', message='Clublog API Key not defined')
        return
    url = "https://secure.clublog.org/cty.php?api={0}".format(config.clublog_api_key)

    try:
        with urllib.request.urlopen(url) as response, open(fname, 'wb') as out_file:
            with gzip.GzipFile(fileobj=response) as uncompressed:
                shutil.copyfileobj(uncompressed, out_file)
    except urllib.error.URLError as err:
        print("!! Error: {0}".format(err))
        exit(-1)
    print("-- File downloaded at {0}".format(fname))

    # Now parse XML file
    tree = None
    try:
        tree = ElementTree.parse(fname)
    except FileNotFoundError as err:
        print("!! Error: {0}".format(err))
        exit(-1)
    except ElementTree.ParseError as err:
        print("!! Error: {0}".format(err))
        exit(-1)

    if not tree:
        exit(-1)

    root = tree.getroot()

    for element in root:
        if element.tag == '{http://www.clublog.org/cty/v1.0}entities':
            print('++ Parsing {0}'.format(element.tag))
            rmed = DxccEntities.query.delete()
            print('-- Cleaned {0} old entries'.format(rmed))
            parse_element(element)

        elif element.tag == '{http://www.clublog.org/cty/v1.0}exceptions':
            print('++ Parsing {0}'.format(element.tag))
            rmed = DxccExceptions.query.delete()
            print('-- Cleaned {0} old entries'.format(rmed))
            parse_element(element)

        elif element.tag == '{http://www.clublog.org/cty/v1.0}prefixes':
            print('++ Parsing {0}'.format(element.tag))
            rmed = DxccPrefixes.query.delete()
            print('-- Cleaned {0} old entries'.format(rmed))
            parse_element(element)


def parse_element(element):
    elements = 0
    for child in element:
        skip = False

        if element.tag == '{http://www.clublog.org/cty/v1.0}entities':
            _obj = DxccEntities()
            _obj.ituz = 999  # We don't have ITUZ in cty.xml so we put 999 in it
        elif element.tag == '{http://www.clublog.org/cty/v1.0}exceptions':
            _obj = DxccExceptions()
        elif element.tag == '{http://www.clublog.org/cty/v1.0}prefixes':
            _obj = DxccPrefixes()
        else:
            return

        if 'record' in child.attrib:
            _obj.record = child.attrib['record']

        for attr in child:
            if attr.tag == '{http://www.clublog.org/cty/v1.0}call':
                _obj.call = attr.text
            elif attr.tag == '{http://www.clublog.org/cty/v1.0}name':
                _obj.name = attr.text
            elif attr.tag == '{http://www.clublog.org/cty/v1.0}prefix':
                _obj.prefix = attr.text
            elif attr.tag == '{http://www.clublog.org/cty/v1.0}entity':
                if attr.text == 'INVALID':
                    skip = True
                _obj.entity = attr.text
            elif attr.tag == '{http://www.clublog.org/cty/v1.0}adif':
                _obj.adif = int(attr.text)
            elif attr.tag == '{http://www.clublog.org/cty/v1.0}cqz':
                _obj.cqz = float(attr.text)
            elif attr.tag == '{http://www.clublog.org/cty/v1.0}cont':
                _obj.cont = attr.text
            elif attr.tag == '{http://www.clublog.org/cty/v1.0}long':
                _obj.long = float(attr.text)
            elif attr.tag == '{http://www.clublog.org/cty/v1.0}lat':
                _obj.lat = float(attr.text)
            elif attr.tag == '{http://www.clublog.org/cty/v1.0}start':
                _obj.start = parser.parse(attr.text)
            elif attr.tag == '{http://www.clublog.org/cty/v1.0}end':
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
    print('-- Committed {0} new elements'.format(elements))


def cron_sync_eqsl():
    print("--- Sending logs to eQSL when requested")
    logs = Log.query.filter(Log.eqsl_qsl_sent == 'R').all()
    config = Config.query.first()
    if not config:
        print("!!! Error: config not found")
        a = Logging()
        a.category = 'CONFIG'
        a.level = 'ERROR'
        a.message = 'Config not found'
        db.session.add(a)
        db.session.commit()
        return

    for log in logs:
        status = eqsl_upload_log(log, config)
        err = UserLogging()
        err.user_id = log.user.id
        err.log_id = log.id
        err.logbook_id = log.logbook.id
        err.category = 'EQSL'

        if status['state'] == 'error':
            err.level = 'ERROR'
            print("!! Error uploading QSO {0} to eQSL: {1}".format(log.id, status['message']))
        elif status['state'] == 'rejected':
            log.eqsl_qsl_sent = 'I'
            print("!! Rejected uploading QSO {0} to eQSL: {1}".format(log.id, status['message']))
        else:
            err.level = 'INFO'

        err.message = status['message'] + '\r\n'

        if 'msgs' in status:
            for i in status['msgs']:
                print("!! {0}: {1}".format(i[0], i[1]))
                err.message += '{0}: {1}\r\n'.format(i[0], i[1])

        if status['state'] == 'success':
            log.eqsl_qsl_sent = 'Y'

        print(status)

        db.session.add(err)
        db.session.commit()
