from datetime import datetime

from aiogram.types import CallbackQuery, LabeledPrice
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from environs import Env

from database.models import TicketPurchase
from shop.states import ShopSG
from sqlalchemy.exc import IntegrityError

FINISHED_KEY = "finished"
env = Env()
env.read_env()


async def next_or_end(event, widget, dialog_manager: DialogManager, *_):
    if dialog_manager.dialog_data.get(FINISHED_KEY):
        await dialog_manager.switch_to(ShopSG.preview)
    else:
        await dialog_manager.next()


async def shop_enter_success(event, widget, dialog_manager: DialogManager, *_):
    count = dialog_manager.find("tickets_count").get_value()

    if count < 1:
        await event.answer("Введено отрицательное число")
        return

    try:
        await next_or_end(event, widget, dialog_manager)

    except IntegrityError:
        await event.answer("Произошла ошибка при проверке значения. Повторите попытку.")


async def shop_enter_result_getter(dialog_manager: DialogManager, **kwargs):
    dialog_manager.dialog_data[FINISHED_KEY] = True

    data = {
        "tickets_count": dialog_manager.find("tickets_count").get_value(),
    }

    return data


async def buy_tickets(call: CallbackQuery, widget, dialog_manager: DialogManager):
    count = int(dialog_manager.find("tickets_count").get_value())
    price_per_ticket = int(env('PRICE_PER_TICKET'))

    session = dialog_manager.middleware_data["session"]

    new_purchase = TicketPurchase(
        user_id=call.from_user.id,
        amount=count,
        price_per_ticket=price_per_ticket,
        purchase_date=datetime.utcnow()
    )

    session.add(new_purchase)
    await session.commit()
    await session.refresh(new_purchase)

    await call.bot.send_invoice(
        call.from_user.id,
        title=f"Покупка {count} тикетов",
        description=f"💹 Текущий курс тикетов: {price_per_ticket} ⭐ = 1 🎫",
        provider_token="",
        payload=str(new_purchase.id),
        currency="XTR",
        prices=[LabeledPrice(label="Тикеты", amount=int(count * price_per_ticket))],
    )
    await dialog_manager.done()

