"""Regenerate all slugs

Revision ID: f60879ce41e1
Revises: 98ea6ef6fc14
Create Date: 2016-08-20 19:21:41.308837

"""

# revision identifiers, used by Alembic.
revision = 'f60879ce41e1'
down_revision = '98ea6ef6fc14'

from models import db, User, Cat, ContestTemplate, Contest, Contact, Logbook, Picture, Log, Note


def upgrade():
    for a in User.query.all():
        a.slug = "{0}-updateme".format(a.id)
    for a in Cat.query.all():
        a.slug = "{0}-updateme".format(a.id)
    for a in ContestTemplate.query.all():
        a.slug = "{0}-updateme".format(a.id)
    for a in Contest.query.all():
        a.slug = "{0}-updateme".format(a.id)
    for a in Contact.query.all():
        a.slug = "{0}-updateme".format(a.id)
    for a in Logbook.query.all():
        a.slug = "{0}-updateme".format(a.id)
    for a in Picture.query.all():
        a.slug = "{0}-updateme".format(a.id)
    for a in Log.query.all():
        a.slug = "{0}-updateme".format(a.id)
    for a in Note.query.all():
        a.slug = "{0}-updateme".format(a.id)

    db.session.commit()


def downgrade():
    pass
