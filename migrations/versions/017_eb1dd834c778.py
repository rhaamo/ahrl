"""Rename qso_comment to qsl_comment

Revision ID: eb1dd834c778
Revises: 71ebbd5fe6de
Create Date: 2016-06-21 08:56:30.584591

"""

# revision identifiers, used by Alembic.
revision = "eb1dd834c778"
down_revision = "71ebbd5fe6de"

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402
from sqlalchemy.dialects import mysql  # noqa: E402


def upgrade():
    op.add_column("log", sa.Column("qsl_comment", sa.UnicodeText(), nullable=True))
    op.drop_column("log", "qso_comment")


def downgrade():
    op.add_column("log", sa.Column("qso_comment", mysql.TEXT(), nullable=True))
    op.drop_column("log", "qsl_comment")
