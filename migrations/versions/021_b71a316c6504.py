"""Add HamQTH flag to QSO log

Revision ID: b71a316c6504
Revises: 96dd40d300ed
Create Date: 2016-07-12 22:39:21.927365

"""

# revision identifiers, used by Alembic.
revision = "b71a316c6504"
down_revision = "96dd40d300ed"

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402


def upgrade():
    op.add_column("log", sa.Column("consolidated_hamqth", sa.Boolean(), nullable=False))


def downgrade():
    op.drop_column("log", "consolidated_hamqth")
