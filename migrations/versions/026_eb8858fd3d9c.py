"""Add missing bands

Revision ID: eb8858fd3d9c
Revises: df93b7d9aa63
Create Date: 2016-08-24 13:07:47.278565

"""

# revision identifiers, used by Alembic.
revision = "eb8858fd3d9c"
down_revision = "df93b7d9aa63"

from models import db, Band


def upgrade():
    db.session.add(Band(name="630m", zone="iaru1", lower=472000, upper=476000))
    db.session.add(Band(name="60m", zone="iaru1", lower=5351500, upper=5366500))
    db.session.commit()


def downgrade():
    pass
