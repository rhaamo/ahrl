from models import user_datastore, Config, Role, Mode, Band


def make_db_seed(db):
    print("== Seeding database")
    db.session.begin(subtransactions=True)
    try:
        seed_config(db)
        seed_users(db)  # after timezones because not null relation
        # also seeds roles admin/user
        seed_modes(db)
        seed_bands(db)
    except:
        db.session.rollback()
        raise


def seed_users(db):
    print("++ Seeding users")
    role_usr = Role(name='user', description='Simple user')
    role_adm = Role(name='admin', description='Admin user')
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
    print("++ Seeding config")
    db.session.add(Config(lotw_download_url='https://p1k.arrl.org/lotwuser/lotwreport.adi',
                          lotw_upload_url='https://p1k.arrl.org/lotwuser/upload',
                          lotw_rcvd_mark='Y',
                          lotw_login_url='https://p1k.arrl.org/lotwuser/default',
                          eqsl_download_url='http://www.eqsl.cc/qslcard/DownloadInBox.cfm',
                          eqsl_rcvd_mark='Y'))
    db.session.commit()


def seed_modes(db):
    print("+++ Seeding modes")
    for i in ['SSB', 'AM', 'FM', 'CW', 'RTTY', 'PSK31', 'PSK63',
              'JT65', 'JT65B', 'JT6C', 'JT6M', 'JT9-1',
              'FSK441', 'JTMS', 'ISCAT', 'PKT', 'SSTV']:
        db.session.add(Mode(mode=i))
    db.session.commit()


def seed_bands(db):
    print("+++ Seeding bands")
    # Usual bands
    db.session.add(Band(name='160m', lower=1000000, upper=2000000))
    db.session.add(Band(name='80m', lower=3000000, upper=4000000))
    db.session.add(Band(name='40m', lower=6000000, upper=8000000))
    db.session.add(Band(name='30m', lower=9000000, upper=11000000))
    db.session.add(Band(name='20m', lower=13000000, upper=15000000))
    db.session.add(Band(name='17m', lower=17000000, upper=19000000))
    db.session.add(Band(name='15m', lower=20000000, upper=22000000))
    db.session.add(Band(name='12m', lower=23000000, upper=25000000))
    db.session.add(Band(name='10m', lower=27000000, upper=30000000))
    db.session.add(Band(name='6m', lower=49000000, upper=52000000))
    db.session.add(Band(name='4m', lower=69000000, upper=71000000))
    db.session.add(Band(name='2m', lower=140000000, upper=150000000))
    db.session.add(Band(name='1.25m', lower=218000000, upper=226000000))
    db.session.add(Band(name='70cm', lower=430000000, upper=440000000))
    db.session.add(Band(name='33cm', lower=900000000, upper=930000000))
    db.session.add(Band(name='23cm', lower=1200000000, upper=1300000000))
    db.session.add(Band(name='13cm', lower=2200000000, upper=2600000000))
    db.session.add(Band(name='9cm', lower=3000000000, upper=4000000000))
    db.session.add(Band(name='6cm', lower=5000000000, upper=6000000000))
    db.session.add(Band(name='3cm', lower=9000000000, upper=11000000000))
    db.session.add(Band(name='1.2cm', lower=23000000000, upper=25000000000))
    db.session.add(Band(name='6mm', lower=46000000000, upper=55000000000))
    db.session.add(Band(name='4mm', lower=75000000000, upper=82000000000))
    db.session.add(Band(name='2.5mm', lower=120000000000, upper=125000000000))
    db.session.add(Band(name='2mm', lower=133000000000, upper=150000000000))
    db.session.add(Band(name='1mm', lower=240000000000, upper=250000000000))
    db.session.add(Band(name='<1mm', lower=250000000000, upper=None))

    # Specific for some modes
    db.session.add(Band(name='160m', modes='SSB', start=1900000))
    db.session.add(Band(name='160m', modes='CW', start=1830000))
    db.session.add(Band(name='160m', modes='PSK31,PSK63,RTTY,JT65', start=1830000))
    db.session.add(Band(name='160m', modes=None, start=1900000))

    db.session.add(Band(name='80m', modes='CW', start=3550000))
    db.session.add(Band(name='80m', modes='PSK31,PSK63,RTTY,JT65', start=3583000))
    db.session.add(Band(name='80m', modes='SSB', start=3700000))
    db.session.add(Band(name='80m', modes=None, start=3700000))

    db.session.add(Band(name='40m', modes='CW', start=7020000))
    db.session.add(Band(name='40m', modes='PSK31,PSK63,RTTY,JT65', start=7040000))
    db.session.add(Band(name='40m', modes='SSB', start=7100000))
    db.session.add(Band(name='40m', modes=None, start=7100000))

    db.session.add(Band(name='30m', modes='CW', start=10120000))
    db.session.add(Band(name='30m', modes='PSK31,PSK63,RTTY,JT65', start=10145000))
    db.session.add(Band(name='30m', modes=None, start=10120000))

    db.session.add(Band(name='20m', modes='CW', start=14020000))
    db.session.add(Band(name='20m', modes='PSK31,PSK63,RTTY,JT65', start=14080000))
    db.session.add(Band(name='20m', modes='SSB', start=14200000))
    db.session.add(Band(name='20m', modes=None, start=14200000))

    db.session.add(Band(name='17m', modes='CW', start=18080000))
    db.session.add(Band(name='17m', modes='PSK31,PSK63,RTTY,JT65', start=18105000))
    db.session.add(Band(name='17m', modes='SSB', start=18130000))
    db.session.add(Band(name='17m', modes=None, start=18130000))

    db.session.add(Band(name='15m', modes='CW', start=21020000))
    db.session.add(Band(name='15m', modes='PSK31,PSK63,RTTY,JT65', start=21080000))
    db.session.add(Band(name='15m', modes='SSB', start=21300000))
    db.session.add(Band(name='15m', modes=None, start=21300000))

    db.session.add(Band(name='12m', modes='CW', start=24900000))
    db.session.add(Band(name='12m', modes='PSK31,PSK63,RTTY,JT65', start=24925000))
    db.session.add(Band(name='12m', modes='SSB', start=24925000))

    db.session.add(Band(name='10m', modes='CW', start=21050000))
    db.session.add(Band(name='10m', modes='PSK31,PSK63,RTTY,JT65', start=28120000))
    db.session.add(Band(name='10m', modes='SSB', start=28300000))
    db.session.add(Band(name='10m', modes=None, start=28300000))

    db.session.add(Band(name='6m', modes='CW', start=50090000))
    db.session.add(Band(name='6m', modes='PSK31,PSK63,RTTY,JT65', start=50230000))
    db.session.add(Band(name='6m', modes='SSB', start=50150000))
    db.session.add(Band(name='6m', modes=None, start=50150000))

    db.session.add(Band(name='4m', modes='CW', start=70200000))
    db.session.add(Band(name='4m', modes='PSK31,PSK63,RTTY,JT65', start=70200000))
    db.session.add(Band(name='4m', modes='SSB', start=70200000))
    db.session.add(Band(name='4m', modes=None, start=70200000))

    db.session.add(Band(name='2m', modes='CW', start=144050000))
    db.session.add(Band(name='2m', modes='PSK31,PSK63,RTTY,JT65', start=144370000))
    db.session.add(Band(name='2m', modes='SSB', start=144300000))
    db.session.add(Band(name='2m', modes=None, start=144300000))

    db.session.add(Band(name='70cm', modes='CW', start=432050000))
    db.session.add(Band(name='70cm', modes='PSK31,RTTY,JT65', start=432088000))
    db.session.add(Band(name='70cm', modes='SSB', start=432200000))
    db.session.add(Band(name='70cm', modes=None, start=432200000))

    db.session.add(Band(name='23cm', modes='CW', start=1296000000))
    db.session.add(Band(name='23cm', modes='PSK31,RTTY,JT65', start=1296138000))
    db.session.add(Band(name='23cm', modes='SSB', start=1296000000))
    db.session.add(Band(name='23cm', modes=None, start=1296000000))

    db.session.add(Band(name='13cm', modes='CW', start=2320800000))
    db.session.add(Band(name='13cm', modes='PSK31,RTTY,JT65', start=2320800000))
    db.session.add(Band(name='13cm', modes='SSB', start=2320800000))
    db.session.add(Band(name='13cm', modes=None, start=2320800000))

    db.session.add(Band(name='9cm', modes='CW', start=3400000000))
    db.session.add(Band(name='9cm', modes='PSK31,RTTY,JT65', start=3410000000))
    db.session.add(Band(name='9cm', modes='SSB', start=3410000000))
    db.session.add(Band(name='9cm', modes=None, start=3410000000))

    db.session.add(Band(name='6cm', modes='CW', start=5670000000))
    db.session.add(Band(name='6cm', modes='PSK31,RTTY,JT65', start=5670000000))
    db.session.add(Band(name='6cm', modes='SSB', start=5670000000))
    db.session.add(Band(name='6cm', modes=None, start=5670000000))

    db.session.add(Band(name='3cm', modes='CW', start=1022500000))
    db.session.add(Band(name='3cm', modes='PSK31,RTTY,JT65', start=1022500000))
    db.session.add(Band(name='3cm', modes='SSB', start=1022500000))
    db.session.add(Band(name='3cm', modes=None, start=1022500000))

    db.session.commit()
