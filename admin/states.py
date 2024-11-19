from aiogram.fsm.state import StatesGroup, State


class AdminMainSG(StatesGroup):
    start = State()


class AdminStatistic(StatesGroup):
    start = State()


class AdminCreateTournament(StatesGroup):
    type = State()
    photo = State()
    name = State()
    price = State()
    number_of_players = State()
    first_place_award = State()
    description = State()
    link = State()
    group_id = State()
    preview = State()
    save = State()


class AdminRefLink(StatesGroup):
    start = State()
    info = State()
    input_name = State()
    preview = State()
    save = State()


class AdminMandatoryTask(StatesGroup):
    channel_id = State()
    channel_link = State()
    preview = State()
    save = State()


class AdminBroadcastSG(StatesGroup):
    photos = State()
    text = State()
    button_text = State()
    button_link = State()
    preview = State()
    send = State()


class AdminActiveTournamentsSG(StatesGroup):
    active_tournaments = State()
    tournament_info = State()
    get_members = State()
    select_winner = State()
    winner_info = State()


class GiveawaySG(StatesGroup):
    name = State()
    photo = State()
    sponsors = State()
    end_type = State()
    end_value = State()
    prize_places = State()
    ticket_rewards = State()
    preview = State()
    confirm = State()


class AddAdminSG(StatesGroup):
    id = State()
    preview = State()
    save = State()


class AddTicketsSG(StatesGroup):
    id = State()
    count = State()
    preview = State()
    save = State()
