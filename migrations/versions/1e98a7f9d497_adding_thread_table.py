"""Adding thread table

Revision ID: 1e98a7f9d497
Revises: 50d93e0d716f
Create Date: 2015-11-30 22:31:24.340000

"""

# revision identifiers, used by Alembic.
revision = '1e98a7f9d497'
down_revision = '50d93e0d716f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('forum',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('subtitle', sa.String(), nullable=True),
    sa.Column('group', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('thread',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=80), nullable=False),
    sa.Column('fk_forum', sa.Integer(), nullable=True),
    sa.Column('thread_author', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['fk_forum'], ['forum.id'], ),
    sa.ForeignKeyConstraint(['thread_author'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_thread_title'), 'thread', ['title'], unique=False)
    op.drop_table('forums')
    op.drop_column(u'users', 'threads')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column(u'users', sa.Column('threads', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_table('forums',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('subtitle', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('group', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=u'forums_pkey'),
    sa.UniqueConstraint('title', name=u'forums_title_key')
    )
    op.drop_index(op.f('ix_thread_title'), table_name='thread')
    op.drop_table('thread')
    op.drop_table('forum')
    ### end Alembic commands ###
