"""Adding preferred landing page

Revision ID: bfb5db76846f
Revises: a13d6eecc6a6
Create Date: 2016-11-19 11:10:49.685000

"""

# revision identifiers, used by Alembic.
revision = 'bfb5db76846f'
down_revision = 'a13d6eecc6a6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('landing_page', sa.String(), nullable=False, default='/'))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'landing_page')
    ### end Alembic commands ###
