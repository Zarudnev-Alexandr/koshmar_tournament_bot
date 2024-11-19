"""added is_finished giveaway

Revision ID: e7f51a9c1b94
Revises: 4bf2e465c2c4
Create Date: 2024-11-15 13:36:56.718737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7f51a9c1b94'
down_revision: Union[str, None] = '4bf2e465c2c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('giveaways', sa.Column('is_finished', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('giveaways', 'is_finished')
    # ### end Alembic commands ###
