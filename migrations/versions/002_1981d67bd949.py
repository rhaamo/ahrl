"""Add contacts table and relation

Revision ID: 1981d67bd949
Revises: 33200cef9060
Create Date: 2016-06-09 10:47:18.401857

"""

# revision identifiers, used by Alembic.
revision = "1981d67bd949"
down_revision = "33200cef9060"

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402


def upgrade():
    op.create_table(
        "contact",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("callsign", sa.String(length=32), nullable=False),
        sa.Column("gridsquare", sa.String(length=32), nullable=True),
        sa.Column("distance", sa.Float(), nullable=True),
        sa.Column("bearing", sa.Float(), nullable=True),
        sa.Column("bearing_star", sa.String(length=32), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("contact")
