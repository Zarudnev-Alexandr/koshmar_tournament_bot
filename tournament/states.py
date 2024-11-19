from aiogram.fsm.state import StatesGroup, State


class TournamentSG(StatesGroup):
    start = State()
    my_tournaments = State()
    my_tournament_info= State()
    list_tournaments = State()
    tournament_info = State()
    enter_tournament = State()

