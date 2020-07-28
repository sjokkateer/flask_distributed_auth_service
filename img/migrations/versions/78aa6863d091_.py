"""empty message

Revision ID: 78aa6863d091
Revises: 
Create Date: 2020-07-28 21:03:56.004485

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '78aa6863d091'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=254), nullable=False),
    sa.Column('image', sa.LargeBinary(), nullable=False),
    sa.Column('uploaded_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('image')
    # ### end Alembic commands ###
