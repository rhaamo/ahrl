"""Add Log.qso_comment

Revision ID: 71ebbd5fe6de
Revises: 4669be672bc4
Create Date: 2016-06-21 08:53:27.310029

"""

# revision identifiers, used by Alembic.
revision = '71ebbd5fe6de'
down_revision = '4669be672bc4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('log', sa.Column('qso_comment', sa.UnicodeText(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('log', 'qso_comment')
    ### end Alembic commands ###
