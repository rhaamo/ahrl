"""Set initial config values

Revision ID: ec756fff4fe9
Revises: 9a1064423873
Create Date: 2016-06-21 09:09:40.522952

"""

# revision identifiers, used by Alembic.
revision = 'ec756fff4fe9'
down_revision = '9a1064423873'

from models import db, Config


def upgrade():
    db.session.add(Config(name='lotw_download_url', value='https://p1k.arrl.org/lotwuser/lotwreport.adi'))
    db.session.add(Config(name='lotw_upload_url', value='https://p1k.arrl.org/lotwuser/upload'))
    db.session.add(Config(name='lotw_rcvd_mark', value='Y'))
    db.session.add(Config(name='lotw_login_url', value='https://p1k.arrl.org/lotwuser/default'))
    db.session.add(Config(name='eqsl_upload_url', value='https://www.eqsl.cc/qslcard/ImportADIF.cfm'))
    db.session.add(Config(name='eqsl_download_url', value='https://www.eqsl.cc/qslcard/DownloadInBox.cfm'))
    db.session.add(Config(name='eqsl_rcvd_mark', value='Y'))
    db.session.commit()


def downgrade():
    Config.query.delete()
    db.session.commit()
