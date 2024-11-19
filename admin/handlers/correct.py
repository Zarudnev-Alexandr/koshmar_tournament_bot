from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Select
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admin.states import AdminCreateTournament, AdminMandatoryTask, AdminBroadcastSG, AdminActiveTournamentsSG, \
    GiveawaySG, AddAdminSG, AddTicketsSG, AdminRefLink
from database import models

FINISHED_KEY = "finished"


async def next_or_end(event, widget, dialog_manager: DialogManager, *_):
    if dialog_manager.dialog_data.get(FINISHED_KEY):
        await dialog_manager.switch_to(AdminCreateTournament.preview)
    else:
        await dialog_manager.next()


async def next_or_end_mandatory_task(event, widget, dialog_manager: DialogManager, *_):
    if dialog_manager.dialog_data.get(FINISHED_KEY):
        await dialog_manager.switch_to(AdminMandatoryTask.preview)
    else:
        await dialog_manager.next()


async def next_or_end_admin_broadcast(event, widget, dialog_manager: DialogManager, *_):
    if dialog_manager.dialog_data.get(FINISHED_KEY):
        await dialog_manager.switch_to(AdminBroadcastSG.preview)
    else:
        await dialog_manager.next()


async def next_or_end_add_admin(event, widget, dialog_manager: DialogManager, *_):
    if dialog_manager.dialog_data.get(FINISHED_KEY):
        await dialog_manager.switch_to(AddAdminSG.preview)
    else:
        await dialog_manager.next()


async def next_or_end_add_ticckets(event, widget, dialog_manager: DialogManager, *_):
    if dialog_manager.dialog_data.get(FINISHED_KEY):
        await dialog_manager.switch_to(AddTicketsSG.preview)
    else:
        await dialog_manager.next()


async def next_or_end_admin_giveaway(event, widget, dialog_manager: DialogManager, *_):
    if dialog_manager.dialog_data.get(FINISHED_KEY):
        await dialog_manager.switch_to(GiveawaySG.preview)
    else:
        await dialog_manager.next()


async def next_or_end_add_ref_link(event, widget, dialog_manager: DialogManager, *_):
    if dialog_manager.dialog_data.get(FINISHED_KEY):
        await dialog_manager.switch_to(AdminRefLink.preview)
    else:
        await dialog_manager.next()


TOURNAMENT_TYPES_MAP = {
    "custom_a": {"title": "Кастомки", "icon": "🪓"},
    "tdm_b": {"title": "ТДМ турниры", "icon": "🗡️"},
    "metro_c": {"title": "Метро турниры", "icon": "🔪"},
}


async def tournament_enter_result_getter(dialog_manager: DialogManager, **kwargs):
    dialog_manager.dialog_data[FINISHED_KEY] = True
    type_key = dialog_manager.find("tournament_type").get_checked()
    type_data = TOURNAMENT_TYPES_MAP.get(type_key, {"title": "Неизвестный", "icon": "❓"})

    data = {
        "type": type_data,
        "name": dialog_manager.find("name").get_value(),
        "price": dialog_manager.find("price").get_value(),
        "number_of_players": dialog_manager.find("number_of_players").get_value(),
        "first_place_award": dialog_manager.find("first_place_award").get_value(),
        "description": dialog_manager.find("description").get_value(),
        "link": dialog_manager.find("link").get_value(),
        "group_id": dialog_manager.find("group_id").get_value(),
        "photo": MediaAttachment(ContentType.PHOTO,
                                 file_id=MediaId(dialog_manager.dialog_data['photo'])),
    }

    return data


async def mandatory_task_enter_result_getter(dialog_manager: DialogManager, **kwargs):
    dialog_manager.dialog_data[FINISHED_KEY] = True

    channel_id = dialog_manager.find("channel_id").get_value()
    try:
        chat = await dialog_manager.middleware_data["bot"].get_chat(channel_id)
        channel_name = chat.title
        dialog_manager.dialog_data['channel_name'] = channel_name
    except Exception as e:
        channel_name = '❗Канал по этому ID не обнаружен❗'

    data = {
        "channel_id": channel_id,
        "channel_link": dialog_manager.find("channel_link").get_value(),
        "channel_name": channel_name,
    }

    return data


async def tournament_selection(
        callback: CallbackQuery,
        widget: Select,
        manager: DialogManager,
        item_id: str
):
    ctx = manager.current_context()
    ctx.dialog_data.update(selected_tournament_id=item_id)
    await manager.switch_to(AdminActiveTournamentsSG.tournament_info)


async def participant_selection(
        callback: CallbackQuery,
        widget: Select,
        manager: DialogManager,
        item_id: str
):
    ctx = manager.current_context()
    ctx.dialog_data.update(selected_winner=item_id)
    await manager.switch_to(AdminActiveTournamentsSG.winner_info)


async def on_sponsors_entered(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    sponsors = []
    lines = message.text.split('\n')

    for line in lines:
        try:
            link, group_id = line.strip()[1:-1].split(',')
            link = link.strip()
            group_id = int(group_id.strip())
            sponsors.append({"link": link, "group_id": group_id})
        except (ValueError, IndexError):
            await message.answer(f"Ошибка в строке: {line}\nПожалуйста, используйте формат: (ссылка, id)")
            return

    if sponsors:
        dialog_manager.dialog_data['sponsors'] = sponsors
        await dialog_manager.next()
    else:
        await message.answer("Пожалуйста, введите хотя бы одного спонсора.")


END_TYPE_MAP = {
    "time": {"title": "По времени", "icon": "⏱️"},
    "participants": {"title": "По количеству участников", "icon": "👥"},
}


async def get_giveaway_data(dialog_manager: DialogManager, **kwargs):
    dialog_manager.dialog_data[FINISHED_KEY] = True

    end_type_key = dialog_manager.find("end_type_radio").get_checked()
    end_type_data = END_TYPE_MAP.get(end_type_key, {"title": "Неизвестный", "icon": "❓"})

    sponsors = dialog_manager.dialog_data.get('sponsors', [])
    sponsors_text = "\n".join(
        [f"- {s['link']} (ID: {s['group_id']})" for s in sponsors]) if sponsors else "Нет спонсоров"

    ticket_rewards = dialog_manager.find("ticket_rewards").get_value()
    ticket_rewards_list = [int(reward.strip()) for reward in ticket_rewards.split(',')]
    prize_places = int(dialog_manager.find("prize_places").get_value())

    # Создаем красивый текст для призовых мест и наград
    rewards_text = ""
    for i, reward in enumerate(ticket_rewards_list, start=1):
        if i == 1:
            place_emoji = "🥇"
        elif i == 2:
            place_emoji = "🥈"
        elif i == 3:
            place_emoji = "🥉"
        else:
            place_emoji = "🏅"
        rewards_text += f"{place_emoji} {i} место: {reward} тикетов\n"

    data = {
        "name": dialog_manager.find("name").get_value(),
        "sponsors": sponsors_text,
        "end_type": f"{end_type_data['icon']} {end_type_data['title']}",
        "end_value": dialog_manager.find("end_value").get_value(),
        "prize_places": prize_places,
        "rewards": rewards_text.strip(),
    }

    preview_text = (
        f"📣 Название: {data['name']}\n\n"
        f"🏆 Спонсоры:\n{data['sponsors']}\n\n"
        f"🔚 Тип окончания: {data['end_type']}\n"
        f"📊 Значение окончания: {data['end_value']}\n"
        f"🎖️ Призовые места и награды:\n{data['rewards']}"
    )

    result = {
        "text": preview_text,
    }

    # Добавляем фото только если оно есть
    photo = dialog_manager.dialog_data.get('photo')
    if photo:
        result["is_photo"] = True
        result["photo"] = MediaAttachment(ContentType.PHOTO, file_id=MediaId(photo))

    return result


async def get_added_admin(dialog_manager: DialogManager, **kwargs):
    dialog_manager.dialog_data[FINISHED_KEY] = True
    admin_id = dialog_manager.find("admin_id_text").get_value()

    session: AsyncSession = dialog_manager.middleware_data.get('session')
    if session is None:
        return {"error": "Сессия не найдена"}

    admin_stmt = select(models.User).filter_by(tg_id=admin_id).limit(1)
    try:
        admin_result = await session.execute(admin_stmt)
        admin = admin_result.scalars().first()

        if admin:
            return {
                "tg_id": admin.tg_id,
                "pubg_id": admin.pubg_id,
                'found': True,
            }
        else:
            return {'not_found': True}

    except Exception as e:
        await session.rollback()
        return {"error": f"Ошибка при старте турнира: {str(e)}"}


async def get_added_tickets(dialog_manager: DialogManager, **kwargs):
    dialog_manager.dialog_data[FINISHED_KEY] = True
    user_id = dialog_manager.find("user_id").get_value()
    tickets_count = dialog_manager.find("tickets_count").get_value()

    session: AsyncSession = dialog_manager.middleware_data.get('session')
    if session is None:
        return {"error": "Сессия не найдена"}

    user_stmt = select(models.User).filter_by(tg_id=user_id).limit(1)
    try:
        user_result = await session.execute(user_stmt)
        user = user_result.scalars().first()

        if user:
            return {
                "user_id": user.tg_id,
                "tickets_count": tickets_count,
                'found': True,
            }
        else:
            return {'not_found': True}

    except Exception as e:
        await session.rollback()
        return {"error": f"Ошибка при старте турнира: {str(e)}"}


async def ref_link_selection(
        callback: CallbackQuery,
        widget: Select,
        manager: DialogManager,
        item_id: str
):
    ctx = manager.current_context()
    ctx.dialog_data.update(selected_ref_link=item_id)
    await manager.switch_to(AdminRefLink.info)


async def ref_link_enter_result_getter(dialog_manager: DialogManager, **kwargs):
    dialog_manager.dialog_data[FINISHED_KEY] = True

    link_name = dialog_manager.find("link_name").get_value()

    data = {
        "link_name": link_name,
    }

    return data


