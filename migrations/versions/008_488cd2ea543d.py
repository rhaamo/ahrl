"""Delete old band plan and add default IARU Zone 1 Band Plan (Will break if QSO already present, see this file for help)

Revision ID: 488cd2ea543d3
Revises: f4d4e3c42eb7
Create Date: 2016-06-13 21:55:03.390082

Help:
    SQLAlchemy will not allow with MySQL to delete with breaking relations so let the upgrade fail
    mysql -u whatever -p
    use ahrl;
    SET FOREIGN_KEY_CHECKS=0;
    TRUNCATE TABLE bands;
    SET FOREIGN_KEY_CHECKS=1;
    exit mysql;
    re-run upgrade, it should pass
"""

# revision identifiers, used by Alembic.
revision = "488cd2ea543d"
down_revision = "f4d4e3c42eb7"

from models import db, Band, Log


def upgrade():
    cleaned = Band.query.delete()
    print("-- Cleaned {0} records".format(cleaned))

    # All IARU1 datas extracted from http://f4eed.wordpress.com/ "Petit Memento Radioamateur et SWL"
    # And wikipedia articles synthetizing IARU Band Plans

    # Add band plan for IARU1
    db.session.add(Band(name="2222m", zone="iaru1", lower=135700, upper=137800))
    db.session.add(Band(name="160m", zone="iaru1", lower=1810000, upper=1850000))
    db.session.add(Band(name="80m", zone="iaru1", lower=3500000, upper=3800000))
    db.session.add(Band(name="40m", zone="iaru1", lower=7000000, upper=7200000))
    db.session.add(Band(name="30m", zone="iaru1", lower=10100000, upper=10150000))
    db.session.add(Band(name="20m", zone="iaru1", lower=14000000, upper=14350000))
    db.session.add(Band(name="17m", zone="iaru1", lower=18068000, upper=18168000))
    db.session.add(Band(name="15m", zone="iaru1", lower=21000000, upper=21450000))
    db.session.add(Band(name="12m", zone="iaru1", lower=24890000, upper=24990000))
    db.session.add(Band(name="10m", zone="iaru1", lower=28000000, upper=29700000))
    db.session.add(Band(name="6m", zone="iaru1", lower=50000000, upper=52000000))
    db.session.add(Band(name="2m", zone="iaru1", lower=144000000, upper=146000000))
    db.session.add(Band(name="70cm", zone="iaru1", lower=430000000, upper=440000000))
    db.session.add(Band(name="23cm", zone="iaru1", lower=1240000000, upper=1300000000))
    db.session.add(Band(name="13cm", zone="iaru1", lower=2300000000, upper=2450000000))
    db.session.add(Band(name="5cm", zone="iaru1", lower=5650000000, upper=5850000000))
    db.session.add(Band(name="3cm", zone="iaru1", lower=10000000000, upper=10500000000))
    db.session.add(Band(name="1,2cm", zone="iaru1", lower=24000000000, upper=24250000000))
    db.session.add(Band(name="6mm", zone="iaru1", lower=47000000000, upper=47200000000))
    db.session.add(Band(name="4mm", zone="iaru1", lower=76000000000, upper=81500000000))
    db.session.add(Band(name="2,4mm", zone="iaru1", lower=122250000000, upper=12300000000))
    db.session.add(Band(name="2mm", zone="iaru1", lower=134000000000, upper=14100000000))
    db.session.add(Band(name="1,2mm", zone="iaru1", lower=241000000000, upper=25000000000))

    # Modes plans for IARU1
    # Only CW on 2222m
    db.session.add(Band(name="2222m", zone="iaru1", modes=None, start=135700))

    db.session.add(Band(name="160m", zone="iaru1", modes="CW", start=1810000))
    db.session.add(Band(name="160m", zone="iaru1", modes="RTTY,PSK31,PSK63,SSTV", start=1838000))
    db.session.add(Band(name="160m", zone="iaru1", modes="SSB,AM", start=1838000))
    db.session.add(Band(name="160m", zone="iaru1", modes=None, start=1810000))

    db.session.add(Band(name="80m", zone="iaru1", modes="CW", start=3500000))
    db.session.add(Band(name="80m", zone="iaru1", modes="RTTY,PSK31,PSK63,SSTV", start=3580000))
    db.session.add(Band(name="80m", zone="iaru1", modes="SSB,AM", start=3600000))
    db.session.add(Band(name="80m", zone="iaru1", modes=None, start=3500000))

    db.session.add(Band(name="40m", zone="iaru1", modes="CW", start=7000000))
    db.session.add(Band(name="40m", zone="iaru1", modes="RTTY,PSK31,PSK63,SSTV", start=7040000))
    db.session.add(Band(name="40m", zone="iaru1", modes="SSB,AM", start=7060000))
    db.session.add(Band(name="40m", zone="iaru1", modes=None, start=7000000))

    db.session.add(Band(name="30m", zone="iaru1", modes="CW", start=10100000))
    db.session.add(Band(name="30m", zone="iaru1", modes="RTTY,PSK31,PSK63", start=10140000))
    db.session.add(Band(name="30m", zone="iaru1", modes=None, start=10100000))

    db.session.add(Band(name="20m", zone="iaru1", modes="CW", start=14000000))
    db.session.add(Band(name="20m", zone="iaru1", modes="RTTY,PSK31,PSK63", start=14070000))
    db.session.add(Band(name="20m", zone="iaru1", modes="SSB,AM", start=14101000))
    db.session.add(Band(name="20m", zone="iaru1", modes=None, start=14000000))

    db.session.add(Band(name="17m", zone="iaru1", modes="CW", start=18068000))
    db.session.add(Band(name="17m", zone="iaru1", modes="RTTY,PSK31,PSK63", start=18095000))
    db.session.add(Band(name="17m", zone="iaru1", modes="SSB,AM", start=18111000))
    db.session.add(Band(name="17m", zone="iaru1", modes=None, start=18068000))

    db.session.add(Band(name="15m", zone="iaru1", modes="CW", start=21000000))
    db.session.add(Band(name="15m", zone="iaru1", modes="RTTY,PSK31,PSK63", start=21070000))
    db.session.add(Band(name="15m", zone="iaru1", modes="SSB,AM,SSTV", start=21151000))
    db.session.add(Band(name="15m", zone="iaru1", modes=None, start=21000000))

    db.session.add(Band(name="12m", zone="iaru1", modes="CW", start=24890000))
    db.session.add(Band(name="12m", zone="iaru1", modes="RTTY,PSK31,PSK63", start=24915000))
    db.session.add(Band(name="12m", zone="iaru1", modes="SSB,AM,SSTV", start=24931000))
    db.session.add(Band(name="12m", zone="iaru1", modes=None, start=24890000))

    db.session.add(Band(name="10m", zone="iaru1", modes="CW", start=28000000))
    db.session.add(Band(name="10m", zone="iaru1", modes="RTTY,PSK31,PSK63", start=28070000))
    db.session.add(Band(name="10m", zone="iaru1", modes="SSB,AM,SSTV", start=28225000))
    db.session.add(Band(name="10m", zone="iaru1", modes="FM,PKT", start=29200000))
    db.session.add(Band(name="10m", zone="iaru1", modes=None, start=28000000))

    db.session.add(Band(name="6m", zone="iaru1", modes="CW", start=50000000))
    db.session.add(Band(name="6m", zone="iaru1", modes="SSB", start=50110000))
    db.session.add(Band(name="6m", zone="iaru1", modes="SSTV", start=50510000))
    db.session.add(Band(name="6m", zone="iaru1", modes="FM", start=50520000))
    db.session.add(Band(name="6m", zone="iaru1", modes="RTTY", start=50600000))
    db.session.add(Band(name="6m", zone="iaru1", modes=None, start=50000000))

    db.session.add(Band(name="2m", zone="iaru1", modes="CW,SSB", start=144025000))
    db.session.add(Band(name="2m", zone="iaru1", modes="FM", start=145000000))
    db.session.add(Band(name="2m", zone="iaru1", modes=None, start=144000000))

    db.session.add(Band(name="70cm", zone="iaru1", modes="FM", start=430250000))
    db.session.add(Band(name="70cm", zone="iaru1", modes="CW,SSB", start=432000000))
    db.session.add(Band(name="70cm", zone="iaru1", modes="PSK31", start=432088000))
    db.session.add(Band(name="70cm", zone="iaru1", modes="SSTV", start=432500000))
    db.session.add(Band(name="70cm", zone="iaru1", modes="RTTY", start=432562500))
    db.session.add(Band(name="70cm", zone="iaru1", modes=None, start=430000000))

    db.session.add(Band(name="23cm", zone="iaru1", modes="FM,SSB,CW", start=1260000000))
    db.session.add(Band(name="23cm", zone="iaru1", modes="RTTY", start=1270000000))
    db.session.add(Band(name="23cm", zone="iaru1", modes="PSK31", start=1296138000))
    db.session.add(Band(name="23cm", zone="iaru1", modes=None, start=1240000000))

    db.session.add(Band(name="13cm", zone="iaru1", modes="CW", start=2320025000))
    db.session.add(Band(name="13cm", zone="iaru1", modes="PSK31", start=2320138000))
    db.session.add(Band(name="13cm", zone="iaru1", modes="LSB", start=2320150000))
    db.session.add(Band(name="13cm", zone="iaru1", modes="FM", start=2321000000))
    db.session.add(Band(name="13cm", zone="iaru1", modes=None, start=2300000000))

    db.session.add(Band(name="5cm", zone="iaru1", modes=None, start=5650000000))

    db.session.add(Band(name="3cm", zone="iaru1", modes="CW,SSB", start=10368000000))
    db.session.add(Band(name="3cm", zone="iaru1", modes=None, start=10000000000))

    db.session.add(Band(name="1,2cm", zone="iaru1", modes=None, start=24000000000))

    db.session.add(Band(name="6mm", zone="iaru1", modes=None, start=47000000000))

    db.session.add(Band(name="4mm", zone="iaru1", modes=None, start=76000000000))

    db.session.add(Band(name="2,4mm", zone="iaru1", modes=None, start=122250000000))

    db.session.add(Band(name="2mm", zone="iaru1", modes=None, start=134000000000))

    db.session.add(Band(name="1,2mm", zone="iaru1", modes=None, start=241000000000))

    db.session.commit()

    # Now re-create relations for Logs
    updated = 0
    for log in db.session.query(Log.id, Log.freq, Log.band_id):
        band = Band.query.filter(Band.start.is_(None), Band.lower <= log.freq, Band.upper >= log.freq).all()
        if not band or len(band) <= 0:
            print("!! Could not get band for QSO ID {0} and frequency {1}. Please check !".format(log.id, log.freq))
            continue
        log.band_id = band[0].id
        updated += 1
    db.session.commit()
    print("-- Updated {0} logs".format(updated))


def downgrade():
    pass
