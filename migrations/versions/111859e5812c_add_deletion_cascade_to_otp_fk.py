"""Add deletion cascade to OTP FK

Revision ID: 111859e5812c
Revises: 3ad3c0708773
Create Date: 2015-11-21 10:56:14.339000

"""

# revision identifiers, used by Alembic.
revision = '111859e5812c'
down_revision = '3ad3c0708773'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(u'otp_fk_userid_fkey', 'otp', type_='foreignkey')
    op.create_foreign_key(None, 'otp', 'users', ['fk_userid'], ['id'], ondelete='cascade')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'otp', type_='foreignkey')
    op.create_foreign_key(u'otp_fk_userid_fkey', 'otp', 'users', ['fk_userid'], ['id'])
    ### end Alembic commands ###
