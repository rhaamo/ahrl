"""Add Clublog API Key and eQSL upload url to Config

Revision ID: 1cfbdbdced17
Revises: eb1dd834c778
Create Date: 2016-06-21 11:06:41.681025

"""

# revision identifiers, used by Alembic.
revision = "1cfbdbdced17"
down_revision = "eb1dd834c778"

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402


def upgrade():
    op.add_column("config", sa.Column("clublog_api_key", sa.String(length=255), nullable=True))
    op.add_column("config", sa.Column("eqsl_upload_url", sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column("config", "eqsl_upload_url")
    op.drop_column("config", "clublog_api_key")
