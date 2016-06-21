"""Rewrite config table scheme

Revision ID: c06161c96541
Revises: eb1dd834c778
Create Date: 2016-06-21 09:06:52.685334

"""

# revision identifiers, used by Alembic.
revision = 'c06161c96541'
down_revision = 'eb1dd834c778'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('config', sa.Column('name', sa.String(length=255), nullable=True))
    op.add_column('config', sa.Column('value', sa.String(length=255), nullable=False))
    op.create_unique_constraint(None, 'config', ['name'])
    op.drop_column('config', 'lotw_rcvd_mark')
    op.drop_column('config', 'lotw_login_url')
    op.drop_column('config', 'lotw_upload_url')
    op.drop_column('config', 'eqsl_download_url')
    op.drop_column('config', 'eqsl_rcvd_mark')
    op.drop_column('config', 'lotw_download_url')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('config', sa.Column('lotw_download_url', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('config', sa.Column('eqsl_rcvd_mark', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('config', sa.Column('eqsl_download_url', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('config', sa.Column('lotw_upload_url', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('config', sa.Column('lotw_login_url', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('config', sa.Column('lotw_rcvd_mark', mysql.VARCHAR(length=255), nullable=True))
    op.drop_constraint(None, 'config', type_='unique')
    op.drop_column('config', 'value')
    op.drop_column('config', 'name')
    ### end Alembic commands ###
