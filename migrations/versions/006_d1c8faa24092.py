"""Remove old DXCC models

Revision ID: d1c8faa24092
Revises: b68e04878516
Create Date: 2016-06-12 13:43:01.516921

"""

# revision identifiers, used by Alembic.
revision = "d1c8faa24092"
down_revision = "b68e04878516"

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402


def upgrade():
    op.drop_table("dxccexceptions")
    op.drop_table("dxcc")
    # WTF alembic you drunk
    # op.create_foreign_key(None, 'log', 'logbook', ['logbook_id'], ['id'])


def downgrade():
    op.drop_constraint(None, "log", type_="foreignkey")
    op.create_table(
        "dxcc",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("prefix", sa.VARCHAR(length=30), nullable=False),
        sa.Column("name", sa.VARCHAR(length=150), nullable=True),
        sa.Column("cqz", sa.FLOAT(), nullable=False),
        sa.Column("ituz", sa.FLOAT(), nullable=False),
        sa.Column("cont", sa.VARCHAR(length=5), nullable=False),
        sa.Column("long", sa.FLOAT(), nullable=False),
        sa.Column("lat", sa.FLOAT(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "dxccexceptions",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("prefix", sa.VARCHAR(length=30), nullable=False),
        sa.Column("name", sa.VARCHAR(length=150), nullable=True),
        sa.Column("cqz", sa.FLOAT(), nullable=False),
        sa.Column("ituz", sa.FLOAT(), nullable=False),
        sa.Column("cont", sa.VARCHAR(length=5), nullable=False),
        sa.Column("long", sa.FLOAT(), nullable=False),
        sa.Column("lat", sa.FLOAT(), nullable=False),
        sa.Column("start", sa.DATETIME(), nullable=False),
        sa.Column("end", sa.DATETIME(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
