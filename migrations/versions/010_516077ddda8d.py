"""Fix some IARU Zone 1 upper frequencies

Revision ID: 516077ddda8d
Revises: 790b9af160b5
Create Date: 2016-06-14 17:09:53.898423

"""

# revision identifiers, used by Alembic.
revision = "516077ddda8d"
down_revision = "790b9af160b5"

from models import db, Band  # noqa: E402


def upgrade():
    b1 = Band.query.filter(Band.upper == 12300000000).one()
    b1.upper = 123000000000
    b2 = Band.query.filter(Band.upper == 14100000000).one()
    b2.upper = 141000000000
    b3 = Band.query.filter(Band.upper == 25000000000).one()
    b3.upper = 250000000000
    db.session.commit()


def downgrade():
    pass
