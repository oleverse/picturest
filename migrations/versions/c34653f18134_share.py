"""Share

Revision ID: c34653f18134
Revises: e5761b6b1d36
Create Date: 2023-07-29 23:09:40.475532

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c34653f18134'
down_revision = 'e5761b6b1d36'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pictures', sa.Column('shared', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('pictures', 'shared')
    # ### end Alembic commands ###
