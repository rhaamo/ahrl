"""Add some indexes

Revision ID: 0222deffc1dd
Revises: 8ddd19e5391a
Create Date: 2016-06-15 22:09:53.293115

"""

# revision identifiers, used by Alembic.
revision = "0222deffc1dd"
down_revision = "8ddd19e5391a"

from alembic import op  # noqa: E402


def upgrade():
    op.create_index("ix_name", "bands", ["name"])
    op.create_index("ix_country", "log", ["country"])


def downgrade():
    pass
