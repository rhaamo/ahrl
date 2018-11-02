"""Add HamQTH user and password

Revision ID: 96dd40d300ed
Revises: 4b8ff69cf574
Create Date: 2016-07-12 22:07:04.069253

"""

# revision identifiers, used by Alembic.
revision = "96dd40d300ed"
down_revision = "4b8ff69cf574"

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402


def upgrade():
    op.add_column("user", sa.Column("hamqth_name", sa.String(length=32), nullable=True))
    op.add_column("user", sa.Column("hamqth_password", sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column("user", "hamqth_password")
    op.drop_column("user", "hamqth_name")
