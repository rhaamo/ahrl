"""Add IARU Zone selector to User profile

Revision ID: 790b9af160b5
Revises: 488cd2ea543d
Create Date: 2016-06-13 23:42:26.495078

"""

# revision identifiers, used by Alembic.
revision = "790b9af160b5"
down_revision = "488cd2ea543d"

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402


def upgrade():
    try:
        op.create_foreign_key(None, "log", "logbook", ["logbook_id"], ["id"])
    except NotImplementedError:
        print("Using SQLITE3 lol no ALTER, good luck.")
    op.add_column("user", sa.Column("zone", sa.String(length=10), nullable=False, server_default="iaru1"))


def downgrade():
    op.drop_column("user", "zone")
    op.drop_constraint(None, "log", type_="foreignkey")
