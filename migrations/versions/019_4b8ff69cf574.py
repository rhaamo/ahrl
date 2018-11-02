"""Add timestamps to Logging tables

Revision ID: 4b8ff69cf574
Revises: 1cfbdbdced17
Create Date: 2016-06-21 15:42:59.364330

"""

# revision identifiers, used by Alembic.
revision = "4b8ff69cf574"
down_revision = "1cfbdbdced17"

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402


def upgrade():
    op.add_column("logging", sa.Column("timestamp", sa.DateTime(), server_default=sa.text("now()"), nullable=True))
    op.add_column("user_logging", sa.Column("timestamp", sa.DateTime(), server_default=sa.text("now()"), nullable=True))


def downgrade():
    op.drop_column("user_logging", "timestamp")
    op.drop_column("logging", "timestamp")
