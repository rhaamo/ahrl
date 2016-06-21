"""Emptying config table

Revision ID: 9a1064423873
Revises: c06161c96541
Create Date: 2016-06-21 09:07:37.783267

"""

# revision identifiers, used by Alembic.
revision = '9a1064423873'
down_revision = 'c06161c96541'

from models import db, Config

def upgrade():
    Config.query.delete()
    db.session.commit()


def downgrade():
    pass
