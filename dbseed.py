from models import user_datastore, Config, Role, Band


def make_db_seed(db):
    print("== Seeding database")
    db.session.begin(subtransactions=True)
    try:
        print("++ Seeding config")
        seed_config(db)
        seed_users(db)  # after timezones because not null relation
        # also seeds roles admin/user
    except:
        db.session.rollback()
        raise


def seed_users(db):
    print("++ Seeding users")
    role_usr = Role()
    role_usr.name = 'user'
    role_usr.description = 'Simple user'

    role_adm = Role()
    role_adm.name = 'admin'
    role_adm.description = 'Admin user'

    db.session.add(role_usr)
    db.session.add(role_adm)

    user_datastore.create_user(
        email='dashie@sigpipe.me',
        password='fluttershy',
        name='toto',
        timezone='UTC',
        roles=[role_adm],
        callsign='N0C4LL',
        locator='JN'
    )
    db.session.commit()
    return


def seed_config(db):
    a = Config(lotw_download_url='https://p1k.arrl.org/lotwuser/lotwreport.adi',
               lotw_upload_url='https://p1k.arrl.org/lotwuser/upload',
               lotw_rcvd_mark='Y',
               lotw_login_url='https://p1k.arrl.org/lotwuser/default',
               eqsl_download_url='https://www.eqsl.cc/qslcard/DownloadInBox.cfm',
               eqsl_upload_url='https://www.eqsl.cc/qslcard/ImportADIF.cfm',
               eqsl_rcvd_mark='Y')
    db.session.add(a)
    db.session.commit()
    db.session.commit()
    # Bug, two commit necessary


#### Only used by tests
def seed_bands(db):
    db.session.add(Band(name='2222m', zone='iaru1', lower=135700, upper=137800))
    db.session.add(Band(name='630m', zone='iaru1', lower=472000, upper=476000))
    db.session.add(Band(name='160m', zone='iaru1', lower=1810000, upper=1850000))
    db.session.add(Band(name='80m', zone='iaru1', lower=3500000, upper=3800000))
    db.session.add(Band(name='60m', zone='iaru1', lower=5351500, upper=5366500))
    db.session.add(Band(name='40m', zone='iaru1', lower=7000000, upper=7200000))
    db.session.add(Band(name='30m', zone='iaru1', lower=10100000, upper=10150000))
    db.session.add(Band(name='20m', zone='iaru1', lower=14000000, upper=14350000))
    db.session.add(Band(name='17m', zone='iaru1', lower=18068000, upper=18168000))
    db.session.add(Band(name='15m', zone='iaru1', lower=21000000, upper=21450000))
    db.session.add(Band(name='12m', zone='iaru1', lower=24890000, upper=24990000))
    db.session.add(Band(name='10m', zone='iaru1', lower=28000000, upper=29700000))
    db.session.add(Band(name='6m', zone='iaru1', lower=50000000, upper=52000000))
    db.session.add(Band(name='2m', zone='iaru1', lower=144000000, upper=146000000))
    db.session.add(Band(name='70cm', zone='iaru1', lower=430000000, upper=440000000))
    db.session.add(Band(name='23cm', zone='iaru1', lower=1240000000, upper=1300000000))
    db.session.add(Band(name='13cm', zone='iaru1', lower=2300000000, upper=2450000000))
    db.session.add(Band(name='5cm', zone='iaru1', lower=5650000000, upper=5850000000))
    db.session.add(Band(name='3cm', zone='iaru1', lower=10000000000, upper=10500000000))
    db.session.add(Band(name='1,2cm', zone='iaru1', lower=24000000000, upper=24250000000))
    db.session.add(Band(name='6mm', zone='iaru1', lower=47000000000, upper=47200000000))
    db.session.add(Band(name='4mm', zone='iaru1', lower=76000000000, upper=81500000000))
    db.session.add(Band(name='2,4mm', zone='iaru1', lower=122250000000, upper=123000000000))
    db.session.add(Band(name='2mm', zone='iaru1', lower=134000000000, upper=141000000000))
    db.session.add(Band(name='1,2mm', zone='iaru1', lower=241000000000, upper=250000000000))

    # Modes plans for IARU1
    # Only CW on 2222m
    db.session.add(Band(name='2222m', zone='iaru1', modes=None, start=135700))

    db.session.add(Band(name='160m', zone='iaru1', modes="CW", start=1810000))
    db.session.add(Band(name='160m', zone='iaru1', modes="RTTY,PSK31,PSK63,SSTV", start=1838000))
    db.session.add(Band(name='160m', zone='iaru1', modes="SSB,AM", start=1838000))
    db.session.add(Band(name='160m', zone='iaru1', modes=None, start=1810000))

    db.session.add(Band(name='80m', zone='iaru1', modes="CW", start=3500000))
    db.session.add(Band(name='80m', zone='iaru1', modes="RTTY,PSK31,PSK63,SSTV", start=3580000))
    db.session.add(Band(name='80m', zone='iaru1', modes="SSB,AM", start=3600000))
    db.session.add(Band(name='80m', zone='iaru1', modes=None, start=3500000))

    db.session.add(Band(name='40m', zone='iaru1', modes="CW", start=7000000))
    db.session.add(Band(name='40m', zone='iaru1', modes="RTTY,PSK31,PSK63,SSTV", start=7040000))
    db.session.add(Band(name='40m', zone='iaru1', modes="SSB,AM", start=7060000))
    db.session.add(Band(name='40m', zone='iaru1', modes=None, start=7000000))

    db.session.add(Band(name='30m', zone='iaru1', modes="CW", start=10100000))
    db.session.add(Band(name='30m', zone='iaru1', modes="RTTY,PSK31,PSK63", start=10140000))
    db.session.add(Band(name='30m', zone='iaru1', modes=None, start=10100000))

    db.session.add(Band(name='20m', zone='iaru1', modes="CW", start=14000000))
    db.session.add(Band(name='20m', zone='iaru1', modes="RTTY,PSK31,PSK63", start=14070000))
    db.session.add(Band(name='20m', zone='iaru1', modes="SSB,AM", start=14101000))
    db.session.add(Band(name='20m', zone='iaru1', modes=None, start=14000000))

    db.session.add(Band(name='17m', zone='iaru1', modes="CW", start=18068000))
    db.session.add(Band(name='17m', zone='iaru1', modes="RTTY,PSK31,PSK63", start=18095000))
    db.session.add(Band(name='17m', zone='iaru1', modes="SSB,AM", start=18111000))
    db.session.add(Band(name='17m', zone='iaru1', modes=None, start=18068000))

    db.session.add(Band(name='15m', zone='iaru1', modes="CW", start=21000000))
    db.session.add(Band(name='15m', zone='iaru1', modes="RTTY,PSK31,PSK63", start=21070000))
    db.session.add(Band(name='15m', zone='iaru1', modes="SSB,AM,SSTV", start=21151000))
    db.session.add(Band(name='15m', zone='iaru1', modes=None, start=21000000))

    db.session.add(Band(name='12m', zone='iaru1', modes="CW", start=24890000))
    db.session.add(Band(name='12m', zone='iaru1', modes="RTTY,PSK31,PSK63", start=24915000))
    db.session.add(Band(name='12m', zone='iaru1', modes="SSB,AM,SSTV", start=24931000))
    db.session.add(Band(name='12m', zone='iaru1', modes=None, start=24890000))

    db.session.add(Band(name='10m', zone='iaru1', modes="CW", start=28000000))
    db.session.add(Band(name='10m', zone='iaru1', modes="RTTY,PSK31,PSK63", start=28070000))
    db.session.add(Band(name='10m', zone='iaru1', modes="SSB,AM,SSTV", start=28225000))
    db.session.add(Band(name='10m', zone='iaru1', modes="FM,PKT", start=29200000))
    db.session.add(Band(name='10m', zone='iaru1', modes=None, start=28000000))

    db.session.add(Band(name='6m', zone='iaru1', modes="CW", start=50000000))
    db.session.add(Band(name='6m', zone='iaru1', modes="SSB", start=50110000))
    db.session.add(Band(name='6m', zone='iaru1', modes="SSTV", start=50510000))
    db.session.add(Band(name='6m', zone='iaru1', modes="FM", start=50520000))
    db.session.add(Band(name='6m', zone='iaru1', modes="RTTY", start=50600000))
    db.session.add(Band(name='6m', zone='iaru1', modes=None, start=50000000))

    db.session.add(Band(name='2m', zone='iaru1', modes="CW,SSB", start=144025000))
    db.session.add(Band(name='2m', zone='iaru1', modes="FM", start=145000000))
    db.session.add(Band(name='2m', zone='iaru1', modes=None, start=144000000))

    db.session.add(Band(name='70cm', zone='iaru1', modes="FM", start=430250000))
    db.session.add(Band(name='70cm', zone='iaru1', modes="CW,SSB", start=432000000))
    db.session.add(Band(name='70cm', zone='iaru1', modes="PSK31", start=432088000))
    db.session.add(Band(name='70cm', zone='iaru1', modes="SSTV", start=432500000))
    db.session.add(Band(name='70cm', zone='iaru1', modes="RTTY", start=432562500))
    db.session.add(Band(name='70cm', zone='iaru1', modes=None, start=430000000))

    db.session.add(Band(name='23cm', zone='iaru1', modes="FM,SSB,CW", start=1260000000))
    db.session.add(Band(name='23cm', zone='iaru1', modes="RTTY", start=1270000000))
    db.session.add(Band(name='23cm', zone='iaru1', modes="PSK31", start=1296138000))
    db.session.add(Band(name='23cm', zone='iaru1', modes=None, start=1240000000))

    db.session.add(Band(name='13cm', zone='iaru1', modes="CW", start=2320025000))
    db.session.add(Band(name='13cm', zone='iaru1', modes="PSK31", start=2320138000))
    db.session.add(Band(name='13cm', zone='iaru1', modes="LSB", start=2320150000))
    db.session.add(Band(name='13cm', zone='iaru1', modes="FM", start=2321000000))
    db.session.add(Band(name='13cm', zone='iaru1', modes=None, start=2300000000))

    db.session.add(Band(name='5cm', zone='iaru1', modes=None, start=5650000000))

    db.session.add(Band(name='3cm', zone='iaru1', modes="CW,SSB", start=10368000000))
    db.session.add(Band(name='3cm', zone='iaru1', modes=None, start=10000000000))

    db.session.add(Band(name='1,2cm', zone='iaru1', modes=None, start=24000000000))

    db.session.add(Band(name='6mm', zone='iaru1', modes=None, start=47000000000))

    db.session.add(Band(name='4mm', zone='iaru1', modes=None, start=76000000000))

    db.session.add(Band(name='2,4mm', zone='iaru1', modes=None, start=122250000000))

    db.session.add(Band(name='2mm', zone='iaru1', modes=None, start=134000000000))

    db.session.add(Band(name='1,2mm', zone='iaru1', modes=None, start=241000000000))

    db.session.commit()
