"""Add slugs columns

Revision ID: 98ea6ef6fc14
Revises: b71a316c6504
Create Date: 2016-08-20 18:03:07.039230

"""

# revision identifiers, used by Alembic.
revision = "98ea6ef6fc14"
down_revision = "b71a316c6504"

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402


def upgrade():
    op.add_column("cat", sa.Column("slug", sa.String(length=255), nullable=True))
    op.create_unique_constraint(None, "cat", ["slug"])
    op.add_column("contact", sa.Column("slug", sa.String(length=255), nullable=True))
    op.create_unique_constraint(None, "contact", ["slug"])
    op.add_column("contest_template", sa.Column("slug", sa.String(length=255), nullable=True))
    op.create_unique_constraint(None, "contest_template", ["slug"])
    op.add_column("contests", sa.Column("slug", sa.String(length=255), nullable=True))
    op.create_unique_constraint(None, "contests", ["slug"])
    op.add_column("log", sa.Column("slug", sa.String(length=255), nullable=True))
    op.create_unique_constraint(None, "log", ["slug"])
    op.add_column("logbook", sa.Column("slug", sa.String(length=255), nullable=True))
    op.create_unique_constraint(None, "logbook", ["slug"])
    op.add_column("notes", sa.Column("slug", sa.String(length=255), nullable=True))
    op.create_unique_constraint(None, "notes", ["slug"])
    op.add_column("picture", sa.Column("slug", sa.String(length=255), nullable=True))
    op.create_unique_constraint(None, "picture", ["slug"])
    op.add_column("user", sa.Column("slug", sa.String(length=255), nullable=True))
    op.create_unique_constraint(None, "user", ["slug"])


def downgrade():
    op.drop_constraint(None, "user", type_="unique")
    op.drop_column("user", "slug")
    op.drop_constraint(None, "picture", type_="unique")
    op.drop_column("picture", "slug")
    op.drop_constraint(None, "notes", type_="unique")
    op.drop_column("notes", "slug")
    op.drop_constraint(None, "logbook", type_="unique")
    op.drop_column("logbook", "slug")
    op.drop_constraint(None, "log", type_="unique")
    op.drop_column("log", "slug")
    op.drop_constraint(None, "contests", type_="unique")
    op.drop_column("contests", "slug")
    op.drop_constraint(None, "contest_template", type_="unique")
    op.drop_column("contest_template", "slug")
    op.drop_constraint(None, "contact", type_="unique")
    op.drop_column("contact", "slug")
    op.drop_constraint(None, "cat", type_="unique")
    op.drop_column("cat", "slug")
