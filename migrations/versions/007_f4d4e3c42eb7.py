"""Add zone column to bands

Revision ID: f4d4e3c42eb7
Revises: d1c8faa24092
Create Date: 2016-06-13 21:53:02.914770

"""

# revision identifiers, used by Alembic.
revision = "f4d4e3c42eb7"
down_revision = "d1c8faa24092"

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402


def upgrade():
    op.add_column("bands", sa.Column("zone", sa.String(length=10), nullable=False, server_default="iaru1"))
    try:
        op.create_foreign_key(None, "log", "logbook", ["logbook_id"], ["id"])
    except NotImplementedError:
        print("Using SQLITE3 lol no ALTER, good luck.")


def downgrade():
    op.drop_constraint(None, "log", type_="foreignkey")
    op.drop_column("bands", "zone")
