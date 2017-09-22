from sqlalchemy import String, INTEGER
"""Change backup_codes to plural in column name, change type to STR(16)

Revision ID: a13d6eecc6a6
Revises: 175613d5f86
Create Date: 2016-08-28 08:28:12.651000

"""

# revision identifiers, used by Alembic.
revision = 'a13d6eecc6a6'
down_revision = '175613d5f86'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('otp', sa.Column('backup_codes', postgresql.ARRAY(String(length=16)), nullable=True))
    op.drop_column('otp', 'backup_code')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('otp', sa.Column('backup_code', postgresql.ARRAY(INTEGER()), autoincrement=False, nullable=True))
    op.drop_column('otp', 'backup_codes')
    ### end Alembic commands ###
