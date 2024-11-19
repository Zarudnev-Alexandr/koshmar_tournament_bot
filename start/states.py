from aiogram.fsm.state import StatesGroup, State


class StartSG(StatesGroup):
    check_registration = State()


class RegistrationSG(StatesGroup):
    start = State()
    pubg_id = State()
    preview = State()
    save = State()


class MenuSG(StatesGroup):
    menu = State()


class ProfileSG(StatesGroup):
    start = State()


class UserGiveawaySG(StatesGroup):
    start = State()
    giveaway_info = State()

