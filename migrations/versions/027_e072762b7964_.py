"""Add old logbook field

Revision ID: e072762b7964
Revises: eb8858fd3d9c
Create Date: 2016-12-22 11:38:09.835930

"""

# revision identifiers, used by Alembic.
revision = "e072762b7964"
down_revision = "eb8858fd3d9c"

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402


def upgrade():
    op.add_column("logbook", sa.Column("old", sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column("logbook", "old")
