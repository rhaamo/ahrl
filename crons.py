from __future__ import print_function
from models import Log
from utils import get_dxcc_from_clublog
import urllib.request
import shutil
import os
import gzip
from flask import current_app
import xml.etree.ElementTree as ET
from models import db, DxccEntities, DxccExceptions, DxccPrefixes
from dateutil import parser


def update_qsos_without_countries(db):
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


def update_dxcc_from_cty_xml(db):
    print("--- Updating DXCC tables (prefixes, entities, exceptions) from cty.xml")
    fname = os.path.join(current_app.config['TEMP_DOWNLOAD_FOLDER'], 'cty.xml')

    if os.path.isfile(fname):
        os.remove(fname)
        print("-- Removed old file {0}".format(fname))

    print("-- Downloading...")
    url = "https://secure.clublog.org/cty.php?api={0}".format(current_app.config['CLUBLOG_API_KEY'])

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
        tree = ET.parse(fname)
    except FileNotFoundError as err:
        print("!! Error: {0}".format(err))
        exit(-1)
    except ET.ParseError as err:
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
        if element.tag == '{http://www.clublog.org/cty/v1.0}entities':
            _type = 'entity'
            _obj = DxccEntities()
            _obj.ituz = 999  # We don't have ITUZ in cty.xml so we put 999 in it
        elif element.tag == '{http://www.clublog.org/cty/v1.0}exceptions':
            _type = 'exception'
            _obj = DxccExceptions()
        elif element.tag == '{http://www.clublog.org/cty/v1.0}prefixes':
            _type = 'prefix'
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

        db.session.add(_obj)
        elements += 1
    db.session.commit()
    print('-- Committed {0} new elements'.format(elements))
