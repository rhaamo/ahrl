"""Add gridsquare cache field

Revision ID: a69619a8fd47
Revises: 0222deffc1dd
Create Date: 2016-06-16 14:20:33.454389

"""

# revision identifiers, used by Alembic.
revision = "a69619a8fd47"
down_revision = "0222deffc1dd"

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402


def upgrade():
    op.drop_index("ix_name", table_name="bands")
    op.add_column("log", sa.Column("cache_gridsquare", sa.String(length=12), nullable=True))
    op.drop_index("ix_country", table_name="log")


def downgrade():
    op.create_index("ix_country", "log", ["country"], unique=False)
    op.drop_column("log", "cache_gridsquare")
    op.create_index("ix_name", "bands", ["name"], unique=False)
