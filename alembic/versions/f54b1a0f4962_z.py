"""z

Revision ID: f54b1a0f4962
Revises: 119b2e73158e
Create Date: 2024-11-13 18:29:27.796799

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f54b1a0f4962'
down_revision: Union[str, None] = '119b2e73158e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mandatory_tasks', sa.Column('channel_name', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('mandatory_tasks', 'channel_name')
    # ### end Alembic commands ###
