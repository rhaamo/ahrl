"""Add Logbook table and relations

Revision ID: dba2c36b8d15
Revises: 1981d67bd949
Create Date: 2016-06-10 12:47:09.216628

"""

# revision identifiers, used by Alembic.
revision = "dba2c36b8d15"
down_revision = "1981d67bd949"

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402


def upgrade():
    op.create_table(
        "logbook",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("callsign", sa.String(length=32), nullable=False),
        sa.Column("locator", sa.String(length=16), nullable=False),
        sa.Column("swl", sa.Boolean(), nullable=True),
        sa.Column("default", sa.Boolean(), nullable=True),
        sa.Column("public", sa.Boolean(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("log", sa.Column("logbook_id", sa.Integer(), nullable=False, server_default="0"))
    try:
        op.create_foreign_key(None, "log", "logbook", ["logbook_id"], ["id"])
        op.alter_column("log", "logbook_id", server_default=None)
    except NotImplementedError:
        print("Using SQLITE3 lol no ALTER, good luck.")


def downgrade():
    op.drop_constraint(None, "log", type_="foreignkey")
    op.drop_column("log", "logbook_id")
    op.drop_table("logbook")
