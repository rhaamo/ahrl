"""Create picture table

Revision ID: 85dc2959dc8c
Revises: eeb294f07948
Create Date: 2016-06-12 00:27:05.157817

"""

# revision identifiers, used by Alembic.
revision = "85dc2959dc8c"
down_revision = "dba2c36b8d15"

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402


def upgrade():
    op.create_table(
        "picture",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=True),
        sa.Column("filesize", sa.Integer(), nullable=True),
        sa.Column("hash", sa.String(length=255), nullable=True),
        sa.Column("log_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["log_id"], ["log.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hash"),
    )
    try:
        op.create_foreign_key(None, "log", "logbook", ["logbook_id"], ["id"])
    except NotImplementedError:
        print("Using SQLITE3 lol no ALTER, good luck.")


def downgrade():
    op.drop_constraint(None, "log", type_="foreignkey")
    op.drop_table("picture")
