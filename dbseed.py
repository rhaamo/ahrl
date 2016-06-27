from models import user_datastore, Config, Role


def make_db_seed(db):
    print("== Seeding database")
    db.session.begin(subtransactions=True)
    try:
        seed_config(db)
        # seed_users(db)  # after timezones because not null relation
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
    print("++ Seeding config")
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
