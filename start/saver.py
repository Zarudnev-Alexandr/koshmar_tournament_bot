import asyncio
import logging
import random
from datetime import timedelta, datetime

from aiogram.types import User, CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import joinedload

from database import models
from database.session import engine
from start.states import UserGiveawaySG


async def save_user(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    tg_id = event_from_user.id
    session: AsyncSession = dialog_manager.middleware_data.get('session')

    inviter_id = None
    if dialog_manager.start_data:
        inviter_id = dialog_manager.start_data.get("inviter_id")

    if session is None:
        return None

    pubg_id = dialog_manager.find("pubg_id").get_value()

    user_data = {
        "tg_id": tg_id,
        "fio": f'{event_from_user.first_name} {event_from_user.last_name}',
        "username": event_from_user.username,
        "pubg_id": pubg_id,
    }

    if inviter_id is not None:
        user_data["invited_tg_id"] = inviter_id

    obj = models.User(**user_data)
    session.add(obj)
    await session.commit()

    return {'pubg_id': pubg_id}


async def join_giveaway(callback: CallbackQuery,
                        button: Button,
                        dialog_manager: DialogManager):
    session: AsyncSession = dialog_manager.middleware_data.get('session')
    tg_id = callback.from_user.id

    if session is None:
        logging.error("Database session is not available in middleware_data")
        return None

    giveaway_id = dialog_manager.dialog_data.get('selected_giveaway_id')

    try:
        giveaway_id = int(giveaway_id)
    except ValueError:
        await callback.message.answer('Некорректный ID розыгрыша.')
        await dialog_manager.switch_to(UserGiveawaySG.start)
        return {"error": "Некорректный ID розыгрыша."}

    giveaway_stmt = select(models.Giveaway).filter_by(id=giveaway_id)

    try:
        result = await session.execute(giveaway_stmt)
        giveaway = result.scalar_one_or_none()

        if giveaway is None:
            await callback.message.answer('Розыгрыш не найден.')
            await dialog_manager.switch_to(UserGiveawaySG.start)
            return {"error": "Розыгрыш не найден."}

        if giveaway.is_finished:
            await callback.message.answer('Розыгрыш уже завершен.')
            await dialog_manager.switch_to(UserGiveawaySG.start)
            return {"error": "Розыгрыш уже завершен."}

        if giveaway.end_type == 'participants':
            current_participants_count_stmt = select(func.count()).select_from(models.GiveawayParticipation).filter_by(
                giveaway_id=giveaway.id)
            current_participants_count_result = await session.execute(current_participants_count_stmt)
            current_participants_count = current_participants_count_result.scalar()

            if current_participants_count >= giveaway.end_value:
                await callback.message.answer(
                    'Достигнуто максимальное количество участников.')
                await dialog_manager.switch_to(UserGiveawaySG.start)
                return {"error": "Достигнуто максимальное количество участников."}

        participation_check_stmt = select(models.GiveawayParticipation).filter_by(user_id=tg_id,
                                                                                  giveaway_id=giveaway.id)
        participation_check_result = await session.execute(participation_check_stmt)
        existing_participation = participation_check_result.scalar_one_or_none()

        if existing_participation is not None:
            await callback.message.answer('Вы уже участвуете в этом розыгрыше.')
            await dialog_manager.switch_to(UserGiveawaySG.start)
            return {"error": "Вы уже участвуете в этом розыгрыше."}

        new_participation = models.GiveawayParticipation(user_id=tg_id, giveaway_id=giveaway.id)
        session.add(new_participation)
        await session.commit()

        # Повторно получаем количество участников после добавления
        current_participants_count_stmt = select(func.count()).select_from(models.GiveawayParticipation).filter_by(
            giveaway_id=giveaway.id)
        current_participants_count_result = await session.execute(current_participants_count_stmt)
        current_participants_count = current_participants_count_result.scalar()

        if current_participants_count >= giveaway.end_value:
            await check_giveaways(dialog_manager.middleware_data['bot'], giveaway.id)

        await callback.message.answer('Вы успешно присоединились к розыгрышу!')
        await dialog_manager.switch_to(UserGiveawaySG.start)
        return {"success": "Вы успешно присоединились к розыгрышу!"}

    except Exception as e:
        await session.rollback()
        logging.error(f"Error in join_giveaway: {e}")
        await callback.message.answer("Произошла ошибка при попытке присоединиться к розыгрышу.")


async def check_giveaways(bot, giveaway_id):
    async_session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_maker() as session:
        giveaway_stmt = select(models.Giveaway).filter_by(id=giveaway_id, is_finished=False)
        result = await session.execute(giveaway_stmt)
        giveaway = result.scalar_one_or_none()

        if giveaway is None:
            logging.warning(f"Розыгрыш с ID {giveaway_id} не найден или уже завершён.")
            return {"error": f"Розыгрыш с ID {giveaway_id} не найден или уже завершён."}

        if giveaway.end_type == 'participants':
            current_participants_count_stmt = (
                select(func.count())
                .select_from(models.GiveawayParticipation)
                .filter(models.GiveawayParticipation.giveaway_id == giveaway.id)
            )
            current_participants_count_result = await session.execute(current_participants_count_stmt)
            current_participants_count = current_participants_count_result.scalar()

            if current_participants_count >= giveaway.end_value:
                await finalize_giveaway(giveaway, session, bot)
                return {"success": f"Розыгрыш {giveaway_id} завершён из-за достижения лимита участников."}

        elif giveaway.end_type == 'time':
            print('zxc this is time!', flush=True)
            end_time = giveaway.created + timedelta(hours=giveaway.end_value)
            # end_time = giveaway.created + timedelta(seconds=5)
            if datetime.now() >= end_time:
                await finalize_giveaway_time(giveaway, session, bot)
                return {"success": f"Розыгрыш {giveaway_id} завершён по времени."}

        return {"info": f"Розыгрыш {giveaway_id} ещё активен."}


async def finalize_giveaway(giveaway: models.Giveaway, session: AsyncSession, bot):
    participants_stmt = (
        select(models.GiveawayParticipation)
        .options(joinedload(models.GiveawayParticipation.user))
        .filter_by(giveaway_id=giveaway.id)
    )
    result = await session.execute(participants_stmt)
    participants = result.unique().scalars().all()

    if not participants:
        return

    random.shuffle(participants)

    rewards = giveaway.ticket_rewards[:giveaway.prize_places]

    results_message = "🏆 Розыгрыш завершен! Результаты:\n\n"
    user_updates = []

    for i, participant in enumerate(participants):
        if i < len(rewards):
            reward = rewards[i]
            results_message += f"{i + 1}. Пользователь с ID {participant.user_id} получил {reward} тикетов.\n"
            user_updates.append({
                'tg_id': participant.user_id,
                'ticket_balance': participant.user.ticket_balance + reward
            })

    await session.execute(
        update(models.User),
        user_updates
    )

    giveaway.is_finished = True
    session.add(giveaway)

    await session.commit()

    async def send_message(user_id):
        try:
            await bot.send_message(user_id, results_message)
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")

    await asyncio.gather(*[send_message(participant.user_id) for participant in participants])


async def finalize_giveaway_time(giveaway: models.Giveaway, session: AsyncSession, bot):
    participants_stmt = (
        select(models.GiveawayParticipation)
        .options(joinedload(models.GiveawayParticipation.user))
        .filter_by(giveaway_id=giveaway.id)
    )
    result = await session.execute(participants_stmt)
    participants = result.unique().scalars().all()

    if not participants:
        return

    random.shuffle(participants)

    actual_winners_count = min(len(participants), len(giveaway.ticket_rewards))
    rewards = giveaway.ticket_rewards[:actual_winners_count]

    results_message = "🏆 Розыгрыш завершен! Результаты:\n\n"
    user_updates = []

    for i, participant in enumerate(participants):
        if i < actual_winners_count:
            reward = rewards[i]
            results_message += f"{i + 1}. Пользователь с ID {participant.user_id} получил {reward} тикетов.\n"
            user_updates.append({
                'tg_id': participant.user_id,
                'ticket_balance': participant.user.ticket_balance + reward
            })
        else:
            results_message += f"• Пользователь с ID {participant.user_id} не получил награду.\n"

    if user_updates:
        await session.execute(
            update(models.User),
            user_updates
        )

    giveaway.is_finished = True
    session.add(giveaway)

    await session.commit()

    async def send_message(user_id):
        try:
            await bot.send_message(user_id, results_message)
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")

    await asyncio.gather(*[send_message(participant.user_id) for participant in participants])

