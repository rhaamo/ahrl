"""Add Logging and UserLogging

Revision ID: 4669be672bc4
Revises: 229e1f2ce062
Create Date: 2016-06-21 08:15:48.785979

"""

# revision identifiers, used by Alembic.
revision = "4669be672bc4"
down_revision = "229e1f2ce062"

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402


def upgrade():
    op.create_table(
        "logging",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=255), nullable=False),
        sa.Column("level", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_logging",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=255), nullable=False),
        sa.Column("level", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("log_id", sa.Integer(), nullable=True),
        sa.Column("logbook_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["log_id"], ["log.id"]),
        sa.ForeignKeyConstraint(["logbook_id"], ["logbook.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("user_logging")
    op.drop_table("logging")
