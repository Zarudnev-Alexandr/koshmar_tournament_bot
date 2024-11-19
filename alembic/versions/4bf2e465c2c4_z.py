"""z

Revision ID: 4bf2e465c2c4
Revises: ab48673a1815
Create Date: 2024-11-15 12:21:37.406858

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4bf2e465c2c4'
down_revision: Union[str, None] = 'ab48673a1815'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем новый столбец sponsors
    op.add_column('giveaways', sa.Column('sponsors', sa.JSON(), nullable=False))

    # Преобразуем ticket_rewards в JSON с использованием выражения USING
    op.alter_column(
        'giveaways',
        'ticket_rewards',
        existing_type=sa.INTEGER(),
        type_=sa.JSON(),
        existing_nullable=False,
        postgresql_using="ticket_rewards::text::json"  # Преобразуем INTEGER в текст, а затем в JSON
    )

    # Делаем photo_url nullable
    op.alter_column(
        'giveaways',
        'photo_url',
        existing_type=sa.VARCHAR(),
        nullable=True
    )

    # Удаляем старый столбец sponsor_links
    op.drop_column('giveaways', 'sponsor_links')


def downgrade() -> None:
    # Восстанавливаем sponsor_links
    op.add_column(
        'giveaways',
        sa.Column('sponsor_links', sa.TEXT(), autoincrement=False, nullable=False)
    )

    # Возвращаем photo_url в состояние non-nullable
    op.alter_column(
        'giveaways',
        'photo_url',
        existing_type=sa.VARCHAR(),
        nullable=False
    )

    # Возвращаем ticket_rewards в тип INTEGER
    op.alter_column(
        'giveaways',
        'ticket_rewards',
        existing_type=sa.JSON(),
        type_=sa.INTEGER(),
        existing_nullable=False,
        postgresql_using="ticket_rewards::jsonb::int"  # Преобразуем обратно из JSON в INTEGER
    )

    # Удаляем sponsors
    op.drop_column('giveaways', 'sponsors')
