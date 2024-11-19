from aiogram.fsm.state import StatesGroup, State


class ShopSG(StatesGroup):
    start = State()
    buy_tickets = State()
    preview = State()
    save = State()
