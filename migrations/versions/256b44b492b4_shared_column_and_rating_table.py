"""empty message

Revision ID: 256b44b492b4
Revises: 9ab9c36a0300
Create Date: 2023-07-31 00:57:27.657877

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '256b44b492b4'
down_revision = '9ab9c36a0300'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rating',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('picture_id', sa.Integer(), nullable=False),
    sa.Column('rate', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['picture_id'], ['pictures.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('pictures', sa.Column('shared', sa.Boolean(), nullable=True))
    op.add_column('pictures', sa.Column('avg_rating', sa.Numeric(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('pictures', 'avg_rating')
    op.drop_column('pictures', 'shared')
    op.drop_table('rating')
    # ### end Alembic commands ###
