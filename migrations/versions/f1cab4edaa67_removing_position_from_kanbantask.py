"""Removing position from KanbanTask

Revision ID: f1cab4edaa67
Revises: c4fc5198048a
Create Date: 2025-03-03 20:45:55.228015

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1cab4edaa67'
down_revision = 'c4fc5198048a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('kanban_task', schema=None) as batch_op:
        batch_op.drop_column('position')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('kanban_task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('position', sa.INTEGER(), nullable=False))

    # ### end Alembic commands ###
