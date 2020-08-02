"""empty message

Revision ID: e186c90de6a7
Revises: e287ae611d4a
Create Date: 2020-08-02 21:10:01.182694

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e186c90de6a7'
down_revision = 'e287ae611d4a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('keys', sa.Column('is_refresh_token_key', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('keys', 'is_refresh_token_key')
    # ### end Alembic commands ###