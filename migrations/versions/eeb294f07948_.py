"""empty message

Revision ID: eeb294f07948
Revises: dba2c36b8d15
Create Date: 2016-06-10 12:59:47.397225

"""

# revision identifiers, used by Alembic.
revision = 'eeb294f07948'
down_revision = 'dba2c36b8d15'

from models import db, Logbook, User


def upgrade():
    for user in User.query.all():
        c = 0
        if Logbook.query.count() <= 0:
            l = Logbook()
            l.name = "Default logbook"
            l.callsign = user.callsign
            l.locator = user.locator
            l.swl = user.swl
            l.public = True
            l.default = True
            l.user_id = user.id

            db.session.add(l)
            db.session.commit()
        logbook = Logbook.query.first()
        for log in user.logs:
            log.logbook_id = logbook.id
            c += 1
        db.session.commit()
        print("Updated user {0}: {1} qsos added to default logbook".format(
            user.callsign, c
        ))


def downgrade():
    pass
