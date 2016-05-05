from __future__ import print_function
from models import Log
from utils import get_dxcc_from_clublog


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
