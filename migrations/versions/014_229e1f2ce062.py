"""Add eQSL Nickname

Revision ID: 229e1f2ce062
Revises: a69619a8fd47
Create Date: 2016-06-21 07:46:24.963938

"""

# revision identifiers, used by Alembic.
revision = "229e1f2ce062"
down_revision = "a69619a8fd47"

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402


def upgrade():
    op.add_column("logbook", sa.Column("eqsl_qth_nickname", sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column("logbook", "eqsl_qth_nickname")
