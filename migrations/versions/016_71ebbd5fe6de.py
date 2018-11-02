"""Add Log.qso_comment

Revision ID: 71ebbd5fe6de
Revises: 4669be672bc4
Create Date: 2016-06-21 08:53:27.310029

"""

# revision identifiers, used by Alembic.
revision = "71ebbd5fe6de"
down_revision = "4669be672bc4"

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402


def upgrade():
    op.add_column("log", sa.Column("qso_comment", sa.UnicodeText(), nullable=True))


def downgrade():
    op.drop_column("log", "qso_comment")
