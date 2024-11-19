from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database import models
from start.states import RegistrationSG, UserGiveawaySG

FINISHED_KEY = "finished"


async def next_or_end(event, widget, dialog_manager: DialogManager, *_):
    if dialog_manager.dialog_data.get(FINISHED_KEY):
        await dialog_manager.switch_to(RegistrationSG.preview)
    else:
        await dialog_manager.next()


async def pubg_id_success(event, widget, dialog_manager: DialogManager, *_):
    text = dialog_manager.find("pubg_id").get_value()
    text = str(text)
    session: AsyncSession = dialog_manager.middleware_data.get('session')

    if not (text.startswith("51") and 8 <= len(text) <= 12):
        await event.answer("Неверный формат PUBG ID. Убедитесь, что он начинается с '51' и имеет от 8 до 12 цифр.")
        return

    # Проверка уникальности pubg_id в базе данных
    try:
        pubg_id = int(text)
        stmt = select(models.User).where(models.User.pubg_id == pubg_id)
        result = await session.execute(stmt)
        existing_user = result.scalars().first()

        if existing_user:
            await event.answer("Этот PUBG ID уже зарегистрирован. Пожалуйста, используйте уникальный PUBG ID.")
            return

        # Если уникален, продолжаем
        await next_or_end(event, widget, dialog_manager)

    except IntegrityError:
        await session.rollback()
        await event.answer("Произошла ошибка при проверке PUBG ID. Повторите попытку.")


async def result_getter(dialog_manager: DialogManager, **kwargs):
    dialog_manager.dialog_data[FINISHED_KEY] = True
    return {
        "pubg_id": dialog_manager.find("pubg_id").get_value(),
    }


async def giveaway_selection(
        callback: CallbackQuery,
        widget: Select,
        manager: DialogManager,
        item_id: str
):
    ctx = manager.current_context()
    ctx.dialog_data.update(selected_giveaway_id=item_id)
    await manager.switch_to(UserGiveawaySG.giveaway_info)
