"""Rename qso_comment to qsl_comment

Revision ID: eb1dd834c778
Revises: 71ebbd5fe6de
Create Date: 2016-06-21 08:56:30.584591

"""

# revision identifiers, used by Alembic.
revision = 'eb1dd834c778'
down_revision = '71ebbd5fe6de'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('log', sa.Column('qsl_comment', sa.UnicodeText(), nullable=True))
    op.drop_column('log', 'qso_comment')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('log', sa.Column('qso_comment', mysql.TEXT(), nullable=True))
    op.drop_column('log', 'qsl_comment')
    ### end Alembic commands ###