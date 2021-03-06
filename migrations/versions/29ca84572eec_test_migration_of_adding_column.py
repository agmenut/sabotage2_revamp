"""Test migration of adding column

Revision ID: 29ca84572eec
Revises: 2bc2afef4a18
Create Date: 2015-10-13 18:59:52.122000

"""

# revision identifiers, used by Alembic.
revision = '29ca84572eec'
down_revision = '2bc2afef4a18'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('threads', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'threads')
    ### end Alembic commands ###
