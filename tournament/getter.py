import asyncio
import logging
from datetime import datetime, timedelta

from aiogram.enums import ContentType
from aiogram.types import User, CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import Button
from apscheduler.triggers.date import DateTrigger
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database import models
from database.models import TournamentType
from database.session import session_maker
from tournament.states import TournamentSG


async def get_all_tournaments(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    tg_id = event_from_user.id
    tournament_type = dialog_manager.dialog_data.get('tournament_type')
    session: AsyncSession = dialog_manager.middleware_data.get('session')

    if session is None:
        logging.error("Database session is not available in middleware_data")
        return None

    all_active_tournaments_stmt = select(models.Tournament).options(
        load_only(models.Tournament.id, models.Tournament.name, )
    ).filter_by(is_active=True, type=tournament_type)

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


async def get_my_tournaments(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    tg_id = event_from_user.id
    session: AsyncSession = dialog_manager.middleware_data.get('session')

    if session is None:
        logging.error("Database session is not available in middleware_data")
        return None

    my_tournaments_stmt = (
        select(models.Tournament)
        .join(models.TournamentParticipation, models.Tournament.id == models.TournamentParticipation.tournament_id)
        .filter(models.TournamentParticipation.user_id == tg_id, models.Tournament.is_active == True)
        .options(load_only(models.Tournament.id, models.Tournament.name))
    )

    try:
        result = await session.execute(my_tournaments_stmt)
        tournaments = result.scalars().all()

        if tournaments:
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
        logging.error(f"Error in get_my_tournaments: {e}")
        return None


TOURNAMENT_TYPES_MAP = {
    TournamentType.CUSTOM: "🪓 Кастомки",
    TournamentType.TDM: "🗡️ ТДМ турниры",
    TournamentType.METRO: "🔪 Метро турниры",
}


async def get_channel_id_from_link(group_link: str, bot):
    try:
        chat = await bot.get_chat(group_link)
        return chat.id
    except Exception as e:
        print(f"Ошибка при получении channel_id из ссылки: {e}")
        return None


# async def get_tournament_info(event_from_user: User, dialog_manager: DialogManager, **kwargs):
#     ctx = dialog_manager.current_context()
#     tournament_id = int(ctx.dialog_data['selected_tournament_id'])
#     session: AsyncSession = dialog_manager.middleware_data.get('session')
#
#     if session is None:
#         return {"error": "Сессия не найдена"}
#
#     tournament_stmt = select(models.Tournament).filter_by(id=tournament_id).limit(1)
#     participation_count_stmt = select(func.count()).select_from(models.TournamentParticipation).filter_by(
#         tournament_id=tournament_id
#     )
#
#     try:
#         result = await session.execute(tournament_stmt)
#         tournament = result.scalars().first()
#
#         if tournament is None:
#             return {"error": "Турнир с данным типом не найден."}
#
#         participation_result = await session.execute(participation_count_stmt)
#         participation_count = participation_result.scalar()
#
#         tournament_type = TOURNAMENT_TYPES_MAP.get(tournament.type)
#         tournament_status = "Начато" if tournament.is_started else "Сбор"
#
#         tournament_info = {
#             'tournament_type': tournament_type,
#             'name': tournament.name,
#             'price_in_tickets': tournament.price_in_tickets,
#             'total_slots': tournament.total_slots,
#             'reward_first_place': tournament.reward_first_place,
#             'description': tournament.description,
#             'group_link': tournament.group_link,
#             'current_participants': participation_count,
#             'status': tournament_status,
#             'photo': MediaAttachment(ContentType.PHOTO, file_id=MediaId(tournament.photo_url))
#         }
#
#         is_full = participation_count >= tournament.total_slots
#
#         return {**tournament_info, 'is_not_full': not is_full,
#                 'is_not_started': True if tournament_status == 'Сбор' else False,
#                 'lets_sum_it_up': True if tournament.is_started else False,}
#
#     except Exception as e:
#         return {"error": f"Ошибка при получении данных о турнире: {str(e)}"}


async def get_tournament_info(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    ctx = dialog_manager.current_context()
    session: AsyncSession = dialog_manager.middleware_data.get('session')

    if session is None:
        return {"error": "Сессия не найдена"}

    tournament_id = ctx.dialog_data.get('selected_tournament_id')

    if tournament_id is None:
        tournament_id = dialog_manager.start_data.get("selected_tournament_id")
        ctx.dialog_data['selected_tournament_id'] = tournament_id

    if tournament_id is None:
        return {"error": "Данные о турнире не найдены"}

    tournament_id = int(tournament_id)

    tournament_stmt = select(models.Tournament).filter_by(id=tournament_id).limit(1)
    participation_count_stmt = select(func.count()).select_from(models.TournamentParticipation).filter_by(
        tournament_id=tournament_id
    )

    try:
        result = await session.execute(tournament_stmt)
        tournament = result.scalars().first()

        print('❌❌❌', tournament, flush=True)

        if tournament is None:
            return {"error": "Турнир не найден."}

        participation_result = await session.execute(participation_count_stmt)
        participation_count = participation_result.scalar()

        tournament_type = TOURNAMENT_TYPES_MAP.get(tournament.type)
        tournament_status = "Начато" if tournament.is_started else "Сбор"

        tournament_info = {
            'tournament_type': tournament_type,
            'name': tournament.name,
            'price_in_tickets': tournament.price_in_tickets,
            'total_slots': tournament.total_slots,
            'reward_first_place': tournament.reward_first_place,
            'description': tournament.description,
            'group_link': tournament.group_link,
            'current_participants': participation_count,
            'status': tournament_status,
            'photo': MediaAttachment(ContentType.PHOTO, file_id=MediaId(tournament.photo_url))
        }

        is_full = participation_count >= tournament.total_slots

        return {
            **tournament_info,
            'is_not_full': not is_full,
            'is_not_started': tournament_status == 'Сбор',
            'lets_sum_it_up': tournament.is_started,
        }

    except Exception as e:
        raise e
        return {"error": f"Ошибка при получении данных о турнире: {str(e)}"}



scheduler = AsyncIOScheduler()


async def check_user_joined_channel(tg_id: int, tournament_id: int, group_id: int, bot):
    async with session_maker() as session:
        try:
            # group_id_full = '-100' + str(group_id)
            # group_id_int = int(group_id_full)
            member = await bot.get_chat_member(chat_id=group_id, user_id=tg_id)

            if member.status not in ('member', 'administrator', 'creator'):
                await session.execute(
                    delete(models.TournamentParticipation).where(
                        models.TournamentParticipation.user_id == tg_id,
                        models.TournamentParticipation.tournament_id == tournament_id
                    )
                )
                await session.commit()

                await bot.send_message(
                    chat_id=tg_id,
                    text='❌ Вы были дисквалифицированы из турнира, так как не присоединились к каналу в течение 5 минут. '
                         'Тикеты возврату не подлежат.'
                )
        except Exception as e:
            print(f"Ошибка при проверке участия пользователя в канале: {e}", flush=True)


def schedule_check_user_joined_channel(tg_id: int, tournament_id: int, group_id: int, bot):
    run_time = datetime.now() + timedelta(minutes=5)
    try:
        scheduler.add_job(
            check_user_joined_channel,
            trigger=DateTrigger(run_date=run_time),
            args=(tg_id, tournament_id, group_id, bot)
        )
        if not scheduler.running:
            scheduler.start()
    except Exception as e:
        print(f"Ошибка при добавлении задачи: {e}", flush=True)


async def check_tournament_enter(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    tg_id = callback.from_user.id
    ctx = dialog_manager.current_context()
    tournament_id = int(ctx.dialog_data['selected_tournament_id'])

    session: AsyncSession = dialog_manager.middleware_data.get('session')
    if session is None:
        return {"error": "Сессия не найдена"}

    tournament_stmt = select(models.Tournament).filter_by(id=tournament_id).limit(1)
    active_participation_stmt = select(models.TournamentParticipation).join(models.Tournament).filter(
        models.TournamentParticipation.user_id == tg_id,
        models.Tournament.is_active == True
    )
    user_stmt = select(models.User).filter_by(tg_id=tg_id).limit(1)

    try:
        tournament_result = await session.execute(tournament_stmt)
        tournament = tournament_result.scalars().first()

        active_participation_result = await session.execute(active_participation_stmt)
        active_participation = active_participation_result.scalars().first()

        user_result = await session.execute(user_stmt)
        user = user_result.scalars().first()

        if tournament is None:
            return {"error": "Турнир с данным типом не найден."}

        if active_participation:
            await callback.message.answer('Вы уже участвуете в другом активном турнире и не можете записаться в новый.')
            await dialog_manager.switch_to(TournamentSG.start)
            return {"error": "Пользователь уже участвует в активном турнире."}

        if tournament.price_in_tickets > user.ticket_balance:
            await callback.message.answer('У вас недостаточно билетов.')
            await dialog_manager.switch_to(TournamentSG.start)
            return {"error": "У вас недостаточно билетов."}

        user.ticket_balance -= tournament.price_in_tickets
        new_participation = models.TournamentParticipation(user_id=tg_id, tournament_id=tournament_id)

        session.add(new_participation)
        await session.commit()

        await callback.message.answer(
            f'✅ Успешная покупка!\n\n'
            f'🔗 Ссылка на вход в группу для участия: {tournament.group_link}\n\n'
            '⚠️ ВНИМАНИЕ! В случае если вы не войдете в группу в течение 5 минут, '
            'вы будете дисквалифицированы из турнира и тикеты возвращены НЕ БУДУТ.\n'
            'Выход из группы, а также распространение ссылки также будут наказуемы.'
        )
        await dialog_manager.switch_to(TournamentSG.start)

        schedule_check_user_joined_channel(tg_id, tournament_id, tournament.group_id, callback.from_user.bot)

    except Exception as e:
        await session.rollback()
        return {"error": f"Ошибка при записи на турнир: {str(e)}"}



