from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select

from tournament.states import TournamentSG


async def tournament_selection(
        callback: CallbackQuery,
        widget: Select,
        manager: DialogManager,
        item_id: str
):
    ctx = manager.current_context()
    ctx.dialog_data.update(selected_tournament_id=item_id)
    await manager.switch_to(TournamentSG.tournament_info)