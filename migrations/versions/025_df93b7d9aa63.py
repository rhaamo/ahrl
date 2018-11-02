"""Remove unused columns

Revision ID: df93b7d9aa63
Revises: 5539ae4bd72a
Create Date: 2016-08-21 17:37:14.235848

"""

# revision identifiers, used by Alembic.
revision = "df93b7d9aa63"
down_revision = "5539ae4bd72a"

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402


def upgrade():
    op.drop_constraint("picture_hash_key", "picture", type_="unique")
    op.drop_column("picture", "hash")
    op.drop_column("picture", "filesize")


def downgrade():
    op.add_column("picture", sa.Column("filesize", sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column("picture", sa.Column("hash", sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.create_unique_constraint("picture_hash_key", "picture", ["hash"])
