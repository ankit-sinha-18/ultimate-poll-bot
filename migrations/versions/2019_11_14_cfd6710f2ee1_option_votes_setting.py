"""option votes setting

Revision ID: cfd6710f2ee1
Revises: b314e45c659e
Create Date: 2019-11-14 16:38:31.109181

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cfd6710f2ee1'
down_revision = 'b314e45c659e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('poll', sa.Column('show_option_votes', sa.Boolean(), server_default='true', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('poll', 'show_option_votes')
    # ### end Alembic commands ###
