import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from aiogram.types import User, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy import select, func, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from admin.handlers.correct import FINISHED_KEY
from admin.states import AdminMainSG, AdminActiveTournamentsSG
from database import models


async def get_admins_statistic(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    tg_id = event_from_user.id
    session: AsyncSession = dialog_manager.middleware_data.get('session')

    if session is None:
        logging.error("Database session is not available in middleware_data")
        return None

    total_users_stmt = select(func.count()).select_from(models.User)
    new_users_stmt = select(func.count()).select_from(models.User).where(
        models.User.created >= datetime.utcnow() - timedelta(days=1)
    )
    completed_tasks_stmt = select(func.count()).select_from(models.User).where(
        models.User.completed_mandatory_task == True
    )

    try:
        total_users = (await session.execute(total_users_stmt)).scalar()
        new_users = (await session.execute(new_users_stmt)).scalar()
        completed_tasks = (await session.execute(completed_tasks_stmt)).scalar()

        return {
            "total_users": total_users,
            "new_users_today": new_users,
            "completed_tasks": completed_tasks,
        }

    except Exception as e:
        await session.rollback()
        logging.error(f"Error in get_statistics: {e}")
        return None


TYPE_KEY = "types"
END_TYPE_KEY = "end_type_key"


@dataclass
class Type:
    id: str
    name: str
    emoji: str


async def get_tournaments_types(**_kwargs):
    return {
        TYPE_KEY: [
            Type("custom_a", "Кастомки", "🪓"),
            Type("tdm_b", "ТДМ турниры", "🗡️"),
            Type("metro_c", "Метро турниры", "🔪"),
        ],
    }


async def get_end_types(**_kwargs):
    return {
        END_TYPE_KEY: [
            Type("time", "По времени", "⏱️"),
            Type("participants", "По количеству участников", "👥"),
        ],
    }


def type_id_getter(type: Type) -> str:
    return type.id


async def get_admin_broadcast(dialog_manager: DialogManager, **kwargs):
    dialog_manager.dialog_data[FINISHED_KEY] = True
    media_group = dialog_manager.dialog_data.get("media_group", MediaGroupBuilder())
    broadcast_text = dialog_manager.find("broadcast_text").get_value()
    button_text = dialog_manager.find("button_text").get_value()
    button_link = dialog_manager.find("button_link").get_value()

    # Получаем список медиа из MediaGroupBuilder
    media_list = media_group.build()
    photo_count = len(media_list)

    if photo_count > 0:

        await dialog_manager.middleware_data['bot'].send_media_group(
            chat_id=dialog_manager.middleware_data['event_from_user'].id, media=media_list)
    # else:
    #     await dialog_manager.event.answer(broadcast_text)

    return {
        "photo_count": photo_count,
        "broadcast_text": broadcast_text,
        "button_text": button_text,
        "button_link": button_link
    }


async def send_broadcast(callback: CallbackQuery,
                         button: Button,
                         dialog_manager: DialogManager):
    session: AsyncSession = dialog_manager.middleware_data.get('session')

    media_group = dialog_manager.dialog_data.get("media_group", MediaGroupBuilder())
    broadcast_text = dialog_manager.find("broadcast_text").get_value()
    button_text = dialog_manager.find("button_text").get_value()
    button_link = dialog_manager.find("button_link").get_value()

    # Получаем список медиа из MediaGroupBuilder
    media_list = media_group.build()
    photo_count = len(media_list)

    if session is None:
        return

    # Получаем список пользователей
    result = await session.execute(
        select(models.User.tg_id).where(
            or_(
                models.User.completed_mandatory_task == True,
                models.User.is_admin == True
            )
        )
    )
    db_users = result.scalars().all()

    # Создаем клавиатуру с кнопкой, если она задана
    kb = None
    if button_text and button_link:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=button_text, url=button_link)]]
        )

    # Создаем задачу для рассылки
    async def send_to_user(user_id):
        try:
            if photo_count > 0:
                await dialog_manager.middleware_data['bot'].send_media_group(chat_id=user_id, media=media_list)
                await dialog_manager.middleware_data['bot'].send_message(chat_id=user_id, text=broadcast_text,
                                                                         reply_markup=kb)
            else:
                await dialog_manager.middleware_data['bot'].send_message(chat_id=user_id, text=broadcast_text,
                                                                         reply_markup=kb)
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")

    # Отправляем сообщения асинхронно для всех пользователей
    tasks = [send_to_user(user) for user in db_users]
    await asyncio.gather(*tasks)

    await dialog_manager.done()
    await dialog_manager.start(state=AdminMainSG.start)


async def get_all_active_tournaments(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    tg_id = event_from_user.id
    session: AsyncSession = dialog_manager.middleware_data.get('session')

    if session is None:
        logging.error("Database session is not available in middleware_data")
        return None

    all_active_tournaments_stmt = select(models.Tournament).options(
        load_only(models.Tournament.id, models.Tournament.name, )
    ).filter_by(is_active=True)

    try:
        result = await session.execute(all_active_tournaments_stmt)
        tournaments = result.scalars().all()

        if len(tournaments) != 0:
            tournaments_data = [
                (item.name, int(item.id)) for item in tournaments
            ]

            return {
                "found": True,
                "tournaments": tournaments_data,
            }

        return {
            "not_found": True,
        }

    except Exception as e:
        await session.rollback()
        logging.error(f"Error in get_statistics: {e}")
        return None


async def start_tournament(callback: CallbackQuery,
                           button: Button,
                           dialog_manager: DialogManager):
    ctx = dialog_manager.current_context()
    tournament_id = int(ctx.dialog_data['selected_tournament_id'])

    session: AsyncSession = dialog_manager.middleware_data.get('session')
    if session is None:
        return {"error": "Сессия не найдена"}

    tournament_stmt = select(models.Tournament).filter_by(id=tournament_id).limit(1)
    try:
        tournament_result = await session.execute(tournament_stmt)
        tournament = tournament_result.scalars().first()

        if tournament:
            tournament.is_started = True
            await session.commit()

            await dialog_manager.switch_to(AdminActiveTournamentsSG.tournament_info)

    except Exception as e:
        await session.rollback()
        return {"error": f"Ошибка при старте турнира: {str(e)}"}


async def delete_tournament(callback: CallbackQuery,
                            button: Button,
                            dialog_manager: DialogManager):
    ctx = dialog_manager.current_context()
    tournament_id = int(ctx.dialog_data['selected_tournament_id'])

    session: AsyncSession = dialog_manager.middleware_data.get('session')
    if session is None:
        return {"error": "Сессия не найдена"}

    try:
        delete_participants_stmt = (
            delete(models.TournamentParticipation)
            .where(models.TournamentParticipation.tournament_id == tournament_id)
        )
        await session.execute(delete_participants_stmt)

        delete_tournament_stmt = (
            delete(models.Tournament)
            .where(models.Tournament.id == tournament_id)
        )
        await session.execute(delete_tournament_stmt)

        await session.commit()

        await dialog_manager.switch_to(AdminActiveTournamentsSG.active_tournaments)
        await callback.message.answer("Турнир и все его участники успешно удалены.")

    except Exception as e:
        await session.rollback()
        logging.error(f"Ошибка при удалении турнира: {e}")
        return {"error": f"Ошибка при удалении турнира: {str(e)}"}


async def get_tournament_members(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: AsyncSession = dialog_manager.middleware_data.get('session')

    if session is None:
        logging.error("Database session is not available in middleware_data")
        return None

    ctx = dialog_manager.current_context()
    tournament_id = int(ctx.dialog_data['selected_tournament_id'])

    tournament_participants_stmt = (
        select(models.User.tg_id, models.User.pubg_id)
        .join(models.TournamentParticipation, models.TournamentParticipation.user_id == models.User.tg_id)
        .filter(models.TournamentParticipation.tournament_id == tournament_id)
    )

    try:
        result = await session.execute(tournament_participants_stmt)
        participants = result.all()

        if participants:
            participants_data = [
                {"tg_id": participant.tg_id, "pubg_id": participant.pubg_id}
                for participant in participants
            ]

            return {
                "found": True,
                "participants": participants_data,
            }

        return {
            "not_found": True,
            "message": "Участники не найдены для данного турнира."
        }

    except Exception as e:
        await session.rollback()
        logging.error(f"Error in get_tournament_members: {e}")
        return {"error": f"Ошибка при получении участников турнира: {str(e)}"}


async def tournament_members_getter(dialog_manager: DialogManager, **kwargs):
    result = await get_tournament_members(dialog_manager.event.from_user, dialog_manager)

    if result.get("found"):
        if result["participants"]:
            members_list = ", ".join([str(participant["pubg_id"]) for participant in result["participants"]])
            return {"members_list": members_list, "found": True}
        else:
            return {"not_found": True}
    else:
        return {"not_found": True}


async def get_winner_info(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: AsyncSession = dialog_manager.middleware_data.get('session')

    if session is None:
        logging.error("Database session is not available in middleware_data")
        return None

    selected_winner = int(dialog_manager.dialog_data['selected_winner'])

    stmt = select(models.User).options(
        load_only(models.User.tg_id, models.User.pubg_id, models.User.username)
    ).filter_by(tg_id=selected_winner)

    try:
        result = await session.execute(stmt)
        user = result.scalars().first()

        return {
            "username": user.username,
            "tg_id": user.tg_id,
            "pubg_id": user.pubg_id,
        }

    except Exception as e:
        logging.error(f"Error in get_user: {e}")
        await session.rollback()
        return None


async def confirm_winner(callback: CallbackQuery,
                         button: Button,
                         dialog_manager: DialogManager, ):
    ctx = dialog_manager.current_context()
    tournament_id = int(ctx.dialog_data['selected_tournament_id'])
    selected_winner = int(ctx.dialog_data['selected_winner'])

    session: AsyncSession = dialog_manager.middleware_data.get('session')
    if session is None:
        return {"error": "Сессия не найдена"}

    tournament_stmt = select(models.Tournament).filter_by(id=tournament_id).limit(1)
    try:
        tournament_result = await session.execute(tournament_stmt)
        tournament = tournament_result.scalars().first()

        if tournament and tournament.is_active:
            winner_stmt = (
                select(models.TournamentParticipation)
                .filter_by(tournament_id=tournament_id, user_id=selected_winner)
                .limit(1)
            )
            winner_result = await session.execute(winner_stmt)
            winner_participation = winner_result.scalars().first()

            if winner_participation:
                winner_participation.is_winner = True

                winner_user_stmt = select(models.User).filter_by(tg_id=selected_winner).limit(1)
                winner_user_result = await session.execute(winner_user_stmt)
                winner_user = winner_user_result.scalars().first()

                if winner_user:
                    winner_user.ticket_balance += tournament.price_in_tickets

                tournament.is_active = False
                await session.commit()

                await dialog_manager.switch_to(AdminActiveTournamentsSG.active_tournaments)

                await callback.bot.send_message(
                    chat_id=winner_user.tg_id,
                    text=(
                        "Поздравляем! Вы стали победителем турнира! 🎉\n"
                        f"Тикеты в количестве {tournament.price_in_tickets} возвращены на ваш баланс. "
                        "Для получения приза свяжитесь с администратором @nemoooo7."
                    )
                )

            else:
                return {"error": "Выбранный участник не найден в данном турнире."}

    except Exception as e:
        await session.rollback()
        logging.error(f"Ошибка при назначении победителя турнира: {e}")
        return {"error": f"Ошибка при назначении победителя: {str(e)}"}


async def get_ref_links(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: AsyncSession = dialog_manager.middleware_data.get('session')

    if session is None:
        logging.error("Database session is not available in middleware_data")
        return {"error": "Ошибка доступа к базе данных"}

    try:
        # Запрос для получения всех реферальных ссылок (организаций)
        ref_links_stmt = (
            select(models.Organization.name.label('link_name'), models.Organization.user_id.label('link_user_id'))
            .join(models.User, models.User.tg_id == models.Organization.user_id)
            .order_by(models.Organization.name)
        )

        result = await session.execute(ref_links_stmt)
        ref_links = result.all()

        if ref_links:
            ref_links_data = [
                {"link_name": link.link_name, "link_user_id": link.link_user_id}
                for link in ref_links
            ]

            return {
                "found": True,
                "ref_links": ref_links_data,
            }

        return {
            "not_found": True,
            "message": "Реферальные ссылки не найдены."
        }

    except Exception as e:
        await session.rollback()
        logging.error(f"Error in get_ref_links: {e}")
        return {"error": f"Ошибка при получении реферальных ссылок: {str(e)}"}


async def get_ref_info(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: AsyncSession = dialog_manager.middleware_data.get('session')

    if session is None:
        return {"error": "Ошибка доступа к базе данных"}

    ctx = dialog_manager.current_context()
    selected_ref_link_id = ctx.dialog_data.get('selected_ref_link')

    if not selected_ref_link_id:
        return {"error": "Реферальная ссылка не выбрана"}

    try:
        # Получаем информацию о выбранной организации и связанном с ней пользователе
        org_info = await session.execute(
            select(models.Organization.name, models.User.tg_id)
            .join(models.User, models.User.tg_id == models.Organization.user_id)
            .filter(models.Organization.user_id == int(selected_ref_link_id))
        )
        org_info = org_info.first()

        if not org_info:
            return {"error": "Информация о выбранной ссылке не найдена"}

        org_name, ref_user_id = org_info

        # Создаем реферальную ссылку
        referral_link = await create_start_link(event_from_user.bot, payload=f'ref-{ref_user_id}', encode=True)

        # Подсчитываем количество зарегистрированных пользователей по этой ссылке
        count_ref_registered = await session.scalar(
            select(func.count())
            .select_from(models.User)
            .filter_by(invited_tg_id=ref_user_id)
        )

        # Подсчитываем количество пользователей, выполнивших обязательную задачу
        count_watch_ad = await session.scalar(
            select(func.count())
            .select_from(models.User)
            .filter_by(invited_tg_id=ref_user_id, completed_mandatory_task=True)
        )

        return {
            "org_name": org_name,
            "ref_link": referral_link,
            "count_ref_registered": count_ref_registered,
            "count_watch_ad": count_watch_ad
        }

    except Exception as e:
        logging.error(f"Error in get_ref_info: {e}")
        return {"error": f"Ошибка при получении информации о реферальной ссылке: {str(e)}"}
