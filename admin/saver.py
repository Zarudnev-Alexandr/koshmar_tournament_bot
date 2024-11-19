import asyncio
import random

from aiogram.types import User, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from admin.scheduler import schedule_start_giveaway
from admin.states import AdminMainSG
from database import models

TOURNAMENT_TYPES_MAP = {
    "custom_a": "CUSTOM",
    "tdm_b": "TDM",
    "metro_c": "METRO",
}


async def save_tournament(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: AsyncSession = dialog_manager.middleware_data.get('session')
    bot = dialog_manager.middleware_data.get('bot')

    if session is None:
        return None

    type_key = dialog_manager.find("tournament_type").get_checked()
    tournament_type = TOURNAMENT_TYPES_MAP.get(type_key)
    name = dialog_manager.find("name").get_value()
    price_in_tickets = dialog_manager.find("price").get_value()
    total_slots = dialog_manager.find("number_of_players").get_value()
    reward_first_place = dialog_manager.find("first_place_award").get_value()
    description = dialog_manager.find("description").get_value()
    group_link = dialog_manager.find("link").get_value()
    group_id = dialog_manager.find("group_id").get_value()
    photo = dialog_manager.dialog_data.get('photo')

    # Создаем новый турнир
    tournament = models.Tournament(
        type=tournament_type,
        name=name,
        price_in_tickets=price_in_tickets,
        total_slots=total_slots,
        reward_first_place=reward_first_place,
        description=description,
        group_link=group_link,
        group_id=group_id,
        photo_url=photo
    )
    session.add(tournament)
    await session.commit()

    # Формируем данные для рассылки
    broadcast_text = (
        f"🏆 Новый турнир: {name}\n\n"
        f"🎮 Тип: {tournament_type}\n"
        f"💰 Цена участия: {price_in_tickets} тикетов\n"
        f"👥 Количество мест: {total_slots}\n"
        f"🥇 Приз за первое место: {reward_first_place}\n\n"
        f"📝 Описание:\n{description}\n\n"
        f"🔗 Ссылка на группу: {group_link}"
    )

    button = InlineKeyboardButton(
        text="♠️ Перейти к турниру",
        callback_data=f"open_tournament:{tournament.id}:{tournament_type}"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])

    # Получаем список пользователей для рассылки
    # result = await session.execute(select(models.User.tg_id))
    # db_users = result.scalars().all()
    result = await session.execute(
        select(models.User.tg_id).where(
            or_(
                models.User.completed_mandatory_task == True,
                models.User.is_admin == True
            )
        )
    )
    db_users = result.scalars().all()

    # Создаем MediaGroupBuilder
    media_group = MediaGroupBuilder()
    if photo:
        media_group.add_photo(media=photo, caption=broadcast_text)

    # Создаем задачу для рассылки
    async def send_to_user(user_id):
        try:
            media_list = media_group.build()
            if media_list:
                await bot.send_media_group(chat_id=user_id, media=media_list)
                # Отправляем клавиатуру отдельным сообщением
                await bot.send_message(chat_id=user_id, text="Выберите действие:", reply_markup=keyboard)
            else:
                # Если медиа нет, отправляем обычное сообщение с клавиатурой
                await bot.send_message(chat_id=user_id, text=broadcast_text, reply_markup=keyboard)
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")

    tasks = [send_to_user(user) for user in db_users]
    await asyncio.gather(*tasks)

    return {
        'tournament_type': tournament_type,
        'name': name,
        'price_in_tickets': price_in_tickets,
        'total_slots': total_slots,
        'reward_first_place': reward_first_place,
        'description': description,
        'group_link': group_link,
        'group_id': group_id,
        'photo': photo
    }


async def save_mandatory_task(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: AsyncSession = dialog_manager.middleware_data.get('session')
    if session is None:
        return None

    channel_id = dialog_manager.find("channel_id").get_value()
    channel_link = dialog_manager.find("channel_link").get_value()
    channel_name = dialog_manager.dialog_data.get('channel_name')

    mandatory_task = models.MandatoryTask(
        channel_id=channel_id,
        channel_link=channel_link,
        channel_name=channel_name
    )

    session.add(mandatory_task)
    await session.commit()

    return {
        'channel_id': channel_id,
        'channel_link': channel_link,
        'channel_name': channel_name
    }


def generate_artificial_id():
    return random.randint(1, 1000000)


async def save_ref_link(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: AsyncSession = dialog_manager.middleware_data.get('session')
    if session is None:
        return None

    link_name = dialog_manager.find("link_name").get_value()

    id = generate_artificial_id()

    new_user = models.User(
        tg_id=id,
        username=link_name,
        fio=link_name,
        pubg_id=id,
    )

    session.add(new_user)
    await session.flush()

    new_org = models.Organization(name=link_name, user_id=new_user.tg_id)
    session.add(new_org)

    await session.commit()

    ref_link = await create_start_link(event_from_user.bot, payload=f'ref-{new_user.tg_id}', encode=True)

    return {
        'org_name': link_name,
        'ref_link': ref_link,
    }


async def save_giveaway(callback: CallbackQuery,
                        button: Button,
                        dialog_manager: DialogManager):
    session: AsyncSession = dialog_manager.middleware_data.get('session')
    bot = dialog_manager.middleware_data.get('bot')

    if session is None:
        return None

    name = dialog_manager.find("name").get_value()
    sponsors = dialog_manager.dialog_data.get('sponsors', [])
    end_type = dialog_manager.find("end_type_radio").get_checked()
    end_value = int(dialog_manager.find("end_value").get_value())
    prize_places = int(dialog_manager.find("prize_places").get_value())
    ticket_rewards = [int(reward.strip()) for reward in dialog_manager.find("ticket_rewards").get_value().split(',')]
    photo = dialog_manager.dialog_data.get('photo')

    # Создаем новый розыгрыш
    giveaway = models.Giveaway(
        name=name,
        sponsors=sponsors,
        end_type=end_type,
        end_value=end_value,
        prize_places=prize_places,
        ticket_rewards=ticket_rewards,
        photo_url=photo
    )
    session.add(giveaway)
    await session.commit()

    # Формируем данные для рассылки
    end_type_text = "По времени" if end_type == 'time' else "По количеству участников"
    end_value_text = f"{end_value} часов" if end_type == 'time' else f"{end_value} участников"

    rewards_text = "\n".join([f"🏅 {i + 1} место: {reward} тикетов" for i, reward in enumerate(ticket_rewards)])

    sponsors_text = "\n".join([f"🔗 {s['link']}" for s in sponsors]) if sponsors else "Нет спонсоров"

    broadcast_text = (
        f"🎉 Новый розыгрыш: {name}\n\n"
        f"🏆 Спонсоры:\n{sponsors_text}\n\n"
        f"🔚 Тип окончания: {end_type_text}\n"
        f"📊 Значение окончания: {end_value_text}\n"
        f"🎖️ Призовые места и награды:\n{rewards_text}\n\n"
    )

    button = InlineKeyboardButton(
        text="🎲 Участвовать в розыгрыше",
        callback_data=f"join_giveaway:{giveaway.id}"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])

    # Получаем список пользователей для рассылки
    result = await session.execute(
        select(models.User.tg_id).where(
            or_(
                models.User.completed_mandatory_task == True,
                models.User.is_admin == True
            )
        )
    )
    db_users = result.scalars().all()

    # Создаем MediaGroupBuilder
    media_group = MediaGroupBuilder()
    if photo:
        media_group.add_photo(media=photo, caption=broadcast_text)

    # Создаем задачу для рассылки
    async def send_to_user(user_id):
        try:
            media_list = media_group.build()
            if media_list:
                await bot.send_media_group(chat_id=user_id, media=media_list)
                # Отправляем клавиатуру отдельным сообщением
                await bot.send_message(chat_id=user_id, text="Выберите действие:", reply_markup=keyboard)
            else:
                # Если медиа нет, отправляем обычное сообщение с клавиатурой
                await bot.send_message(chat_id=user_id, text=broadcast_text, reply_markup=keyboard)
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")

    # Выполняем рассылку
    tasks = [send_to_user(user) for user in db_users]
    await asyncio.gather(*tasks)

    await dialog_manager.done()
    await dialog_manager.start(state=AdminMainSG.start)

    schedule_start_giveaway(giveaway, callback.from_user.bot)

    return {
        'name': name,
        'sponsors': sponsors,
        'end_type': end_type,
        'end_value': end_value,
        'prize_places': prize_places,
        'ticket_rewards': ticket_rewards,
        'photo': photo
    }


async def save_added_admin(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: AsyncSession = dialog_manager.middleware_data.get('session')

    if session is None:
        return None

    admin_id = dialog_manager.find("admin_id_text").get_value()

    admin_stmt = select(models.User).filter_by(tg_id=admin_id).limit(1)
    try:
        admin_result = await session.execute(admin_stmt)
        admin = admin_result.scalars().first()

        if admin:
            admin.is_admin = True
            await session.commit()

    except Exception as e:
        await session.rollback()
        return {"error": f"Ошибка при добавлении админа: {str(e)}"}

    return {
        'tg_id': admin.tg_id,
    }


async def save_added_tickets(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: AsyncSession = dialog_manager.middleware_data.get('session')

    if session is None:
        return None

    user_id = dialog_manager.find("user_id").get_value()
    tickets_count = dialog_manager.find("tickets_count").get_value()

    user_stmt = select(models.User).filter_by(tg_id=user_id).limit(1)
    try:
        user_result = await session.execute(user_stmt)
        user = user_result.scalars().first()

        if user:
            user.ticket_balance += tickets_count
            await session.commit()

    except Exception as e:
        await session.rollback()
        return {"error": f"Ошибка при добавлении админа: {str(e)}"}

    return {
        'user_id': user.tg_id,
        'tickets_count': tickets_count,
    }
