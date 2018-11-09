"""new fields in user model

Revision ID: cc86890a3110
Revises: e417e6677cd7
Create Date: 2018-11-09 07:53:38.445910

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc86890a3110'
down_revision = 'e417e6677cd7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('customer', sa.Column('timestamp', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_customer_timestamp'), 'customer', ['timestamp'], unique=False)
    op.add_column('project', sa.Column('timestamp', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_project_timestamp'), 'project', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_project_timestamp'), table_name='project')
    op.drop_column('project', 'timestamp')
    op.drop_index(op.f('ix_customer_timestamp'), table_name='customer')
    op.drop_column('customer', 'timestamp')
    # ### end Alembic commands ###
