"""Add TSVector FullTextSearch

Revision ID: 5539ae4bd72a
Revises: f60879ce41e1
Create Date: 2016-08-20 22:56:36.905104

"""

# revision identifiers, used by Alembic.
revision = "5539ae4bd72a"
down_revision = "98ea6ef6fc14"

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402
import sqlalchemy_utils  # noqa: E402
from sqlalchemy_searchable import sync_trigger  # noqa: E402


def upgrade():
    conn = op.get_bind()
    op.add_column("log", sa.Column("search_vector", sqlalchemy_utils.types.ts_vector.TSVectorType(), nullable=True))
    op.create_index("ix_log_search_vector", "log", ["search_vector"], unique=False, postgresql_using="gin")
    sync_trigger(
        conn,
        "log",
        "search_vector",
        [
            "call",
            "comment",
            "country",
            "email",
            "name",
            "notes",
            "operator",
            "owner_callsign",
            "qslmsg",
            "station_callsign",
            "web",
            "qsl_comment",
        ],
    )


def downgrade():
    op.drop_index("ix_log_search_vector", table_name="log")
    op.drop_column("log", "search_vector")
