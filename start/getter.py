import logging
from datetime import datetime, timedelta
from typing import Any

from aiogram.enums import ContentType
from aiogram.types import User
from aiogram.utils.deep_linking import create_start_link
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from database import models
from start.states import StartSG, RegistrationSG, MenuSG


async def get_user_when_entered(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    tg_id = event_from_user.id
    session: AsyncSession = dialog_manager.middleware_data.get('session')

    if session is None:
        logging.error("Database session is not available in middleware_data")
        return None

    stmt = select(models.User).options(
        load_only(models.User.tg_id, models.User.is_admin, models.User.username)
    ).filter_by(tg_id=tg_id)

    try:
        result = await session.execute(stmt)
        user = result.scalars().first()

        return {'new_user': not user, 'old_user': bool(user)}

    except Exception as e:
        logging.error(f"Error in get_user: {e}")
        await session.rollback()
        return None


async def get_entered_pubg_id(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    return {'pubg_id': dialog_manager.dialog_data.get('pubg_id')}


async def get_menu(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    tg_id = event_from_user.id
    bot = dialog_manager.middleware_data['bot']
    session: AsyncSession = dialog_manager.middleware_data.get('session')

    if session is None:
        logging.error("Database session is not available in middleware_data")
        return None

    # Проверка, является ли пользователь администратором
    stmt = select(models.User).options(load_only(models.User.is_admin)).filter_by(tg_id=tg_id)

    try:
        result = await session.execute(stmt)
        user = result.scalars().first()

        if user and user.is_admin:
            return {'admin_user': True, 'subscribe': True}

    except Exception as e:
        logging.error(f"Error checking admin status: {e}")
        await session.rollback()
        return None

    # Если пользователь не администратор, проверяем его подписку на каналы
    all_channels_stmt = select(models.MandatoryTask)
    try:
        result = await session.execute(all_channels_stmt)
        channels = result.scalars().all()
        channels_data = []

        for item in channels:
            user_channel_status = await bot.get_chat_member(chat_id=item.channel_id, user_id=event_from_user.id)
            status = user_channel_status.status

            if status not in ['creator', 'member']:
                channels_data.append({
                    "id": int(item.id),
                    "name": item.channel_name,
                    "url": f'{item.channel_link}'
                })

        if channels_data:
            await dialog_manager.event.answer("Вы все еще не подписались)")
            return {'not_subscribe': True, 'channels': channels_data}
        else:
            user.completed_mandatory_task = True

            await session.commit()
            return {'subscribe': True}

    except Exception as e:
        logging.error(f"Error checking subscription status: {e}")
        await session.rollback()
        return None


async def get_profile(event_from_user: User, dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    tg_id = event_from_user.id
    session: AsyncSession = dialog_manager.middleware_data.get('session')

    if session is None:
        return {"error": "Сессия не найдена"}

    try:
        user_stmt = select(models.User).filter_by(tg_id=tg_id).limit(1)
        user_result = await session.execute(user_stmt)
        user = user_result.scalars().first()

        if user is None:
            return {"error": "Пользователь не найден."}

        tournaments_count_stmt = select(func.count()).select_from(models.TournamentParticipation).filter_by(
            user_id=user.tg_id)
        tournaments_count_result = await session.execute(tournaments_count_stmt)
        tournaments_count = tournaments_count_result.scalar()

        wins_count_stmt = select(func.count()).select_from(models.TournamentParticipation).filter_by(user_id=user.tg_id,
                                                                                                     is_winner=True)
        wins_count_result = await session.execute(wins_count_stmt)
        wins_count = wins_count_result.scalar()

        referrals_count_stmt = select(func.count()).select_from(models.User).filter_by(invited_tg_id=user.tg_id)
        referrals_count_result = await session.execute(referrals_count_stmt)
        referrals_count = referrals_count_result.scalar()

        referral_link = await create_start_link(event_from_user.bot, payload=f'ref-{user.tg_id}', encode=True)

        # Подготовка данных для вывода
        profile_data = {
            "tg_id": user.tg_id,
            "pubg_id": user.pubg_id,
            "tickets": user.ticket_balance,
            "referral_link": referral_link,
            "referrals_count": referrals_count,
            "count_of_tournaments": tournaments_count,
            "count_of_win": wins_count
        }

        # Логирование данных для отладки
        print("Профильные данные:", profile_data)

        return profile_data

    except Exception as e:
        print(f"Ошибка при получении данных профиля: {str(e)}")
        return {"error": f"Ошибка при получении данных профиля: {str(e)}"}


async def get_all_giveaways(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: AsyncSession = dialog_manager.middleware_data.get('session')

    if session is None:
        logging.error("Database session is not available in middleware_data")
        return None

    all_active_giveaways_stmt = select(models.Giveaway).options(
        load_only(models.Giveaway.id, models.Giveaway.name)
    ).filter_by(is_finished=False)

    try:
        result = await session.execute(all_active_giveaways_stmt)
        giveaways = result.scalars().all()

        if giveaways:
            giveaways_data = [
                {
                    "id": giveaway.id,
                    "name": giveaway.name,
                }
                for giveaway in giveaways
            ]

            return {
                "found": True,
                "giveaways": giveaways_data,
            }

        return {
            "not_found": True,
        }

    except Exception as e:
        await session.rollback()
        logging.error(f"Error in get_all_giveaways: {e}")
        return None


async def get_user_giveaway_data(dialog_manager: DialogManager, **kwargs):
    session: AsyncSession = dialog_manager.middleware_data.get('session')
    bot = dialog_manager.middleware_data['bot']

    if session is None:
        logging.error("Database session is not available in middleware_data")
        return None

    giveaway_id = dialog_manager.dialog_data.get('selected_giveaway_id')

    if giveaway_id is None:
        giveaway_id = dialog_manager.start_data.get("selected_giveaway_id")
        dialog_manager.dialog_data['selected_giveaway_id'] = giveaway_id

    if giveaway_id is None:
        logging.error("Giveaway ID is not found in dialog data")
        return None

    # Запрос на получение данных о розыгрыше
    giveaway_stmt = select(models.Giveaway).filter_by(id=int(giveaway_id))

    try:
        result = await session.execute(giveaway_stmt)
        giveaway = result.scalar_one_or_none()

        if giveaway is None:
            return {
                "text": "Розыгрыш не найден.",
                "is_photo": False,
            }

        # Формируем текстовую информацию о розыгрыше
        ticket_rewards_list = giveaway.ticket_rewards
        rewards_text = ""
        for i, reward in enumerate(ticket_rewards_list, start=1):
            place_emoji = {
                1: "🥇",
                2: "🥈",
                3: "🥉"
            }.get(i, "🏅")
            rewards_text += f"{place_emoji} {i} место: {reward} тикетов\n"

        # Определяем текст окончания розыгрыша
        if giveaway.end_type == 'time':
            end_time = giveaway.created + timedelta(hours=giveaway.end_value)
            time_remaining = end_time - datetime.now()

            if time_remaining.total_seconds() > 0:
                hours_remaining, remainder = divmod(time_remaining.total_seconds(), 3600)
                minutes_remaining = remainder // 60

                end_text = f"Окончание через {int(hours_remaining)} ч. {int(minutes_remaining)} мин."
            else:
                end_text = "Розыгрыш уже завершен."
        elif giveaway.end_type == 'participants':
            end_text = f"Окончание при наборе {giveaway.end_value} участников."
        else:
            end_text = "Неизвестный тип окончания."

        preview_text = (
            f"📣 Название: {giveaway.name}\n\n"
            f"🔚 {end_text}\n\n"
            f"🎖️ Призовые места и награды:\n{rewards_text.strip()}"
        )

        result_data = {
            "text": preview_text,
            "is_photo": bool(giveaway.photo_url),
        }

        # Проверка подписки на каналы спонсоров
        sponsors = giveaway.sponsors
        not_subscribed_channels = []

        for sponsor in sponsors:
            try:
                user_channel_status = await bot.get_chat_member(chat_id=sponsor['group_id'],
                                                                user_id=dialog_manager.event.from_user.id)
                status = user_channel_status.status

                if status not in ['creator', 'member']:
                    # Получаем название канала
                    channel_info = await bot.get_chat(sponsor['group_id'])
                    channel_name = channel_info.title

                    not_subscribed_channels.append({
                        "name": channel_name,  # Используем название канала
                        "url": sponsor['link'],
                    })
            except Exception as e:
                logging.error(f"Error checking subscription status for channel {sponsor['link']}: {e}")

        if not_subscribed_channels:
            result_data['not_subscribe'] = True
            result_data['channels'] = not_subscribed_channels
            await dialog_manager.event.answer("Вы все еще не подписались на спонсоров")
        else:
            result_data['subscribed'] = True

        # Добавляем фото только если оно есть
        if giveaway.photo_url:
            result_data["photo"] = MediaAttachment(ContentType.PHOTO, file_id=MediaId(giveaway.photo_url))

        return result_data

    except Exception as e:
        await session.rollback()
        logging.error(f"Error in get_user_giveaway_data: {e}")
        return None

