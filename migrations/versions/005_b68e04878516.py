"""Add new DXCC models

Revision ID: b68e04878516
Revises: 85dc2959dc8c
Create Date: 2016-06-12 11:55:50.658850

"""

# revision identifiers, used by Alembic.
revision = "b68e04878516"
down_revision = "85dc2959dc8c"

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402


def upgrade():
    op.create_table(
        "dxcc_entities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("adif", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=True),
        sa.Column("prefix", sa.String(length=30), nullable=False),
        sa.Column("cqz", sa.Float(), nullable=False),
        sa.Column("ituz", sa.Float(), nullable=False),
        sa.Column("cont", sa.String(length=5), nullable=False),
        sa.Column("long", sa.Float(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("start", sa.DateTime(), nullable=True),
        sa.Column("end", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dxcc_entities_adif"), "dxcc_entities", ["adif"], unique=False)
    op.create_table(
        "dxcc_exceptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("record", sa.Integer(), nullable=False),
        sa.Column("call", sa.String(length=30), nullable=True),
        sa.Column("entity", sa.String(length=255), nullable=False),
        sa.Column("adif", sa.Integer(), nullable=False),
        sa.Column("cqz", sa.Float(), nullable=False),
        sa.Column("cont", sa.String(length=5), nullable=True),
        sa.Column("long", sa.Float(), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("start", sa.DateTime(), nullable=True),
        sa.Column("end", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dxcc_exceptions_record"), "dxcc_exceptions", ["record"], unique=False)
    op.create_table(
        "dxcc_prefixes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("record", sa.Integer(), nullable=False),
        sa.Column("call", sa.String(length=30), nullable=True),
        sa.Column("entity", sa.String(length=255), nullable=False),
        sa.Column("adif", sa.Integer(), nullable=False),
        sa.Column("cqz", sa.Float(), nullable=False),
        sa.Column("cont", sa.String(length=5), nullable=True),
        sa.Column("long", sa.Float(), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("start", sa.DateTime(), nullable=True),
        sa.Column("end", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dxcc_prefixes_record"), "dxcc_prefixes", ["record"], unique=False)
    try:
        op.create_foreign_key(None, "log", "logbook", ["logbook_id"], ["id"])
    except NotImplementedError:
        print("Using SQLITE3 lol no ALTER, good luck.")


def downgrade():
    op.drop_constraint(None, "log", type_="foreignkey")
    op.drop_index(op.f("ix_dxcc_prefixes_record"), table_name="dxcc_prefixes")
    op.drop_table("dxcc_prefixes")
    op.drop_index(op.f("ix_dxcc_exceptions_record"), table_name="dxcc_exceptions")
    op.drop_table("dxcc_exceptions")
    op.drop_index(op.f("ix_dxcc_entities_adif"), table_name="dxcc_entities")
    op.drop_table("dxcc_entities")
