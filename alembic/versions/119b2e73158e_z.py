"""z

Revision ID: 119b2e73158e
Revises: f6c6a43d300d
Create Date: 2024-11-13 17:47:07.367688

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '119b2e73158e'
down_revision: Union[str, None] = 'f6c6a43d300d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mandatory_tasks',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('channel_id', sa.BigInteger(), nullable=False),
    sa.Column('channel_link', sa.String(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mandatory_tasks_channel_id'), 'mandatory_tasks', ['channel_id'], unique=True)
    op.add_column('tournaments', sa.Column('is_started', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tournaments', 'is_started')
    op.drop_index(op.f('ix_mandatory_tasks_channel_id'), table_name='mandatory_tasks')
    op.drop_table('mandatory_tasks')
    # ### end Alembic commands ###