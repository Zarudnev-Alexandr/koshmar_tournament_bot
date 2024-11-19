from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from ad.states import AdSG
from admin.states import AdminMainSG, AdminStatistic, AdminCreateTournament, AdminRefLink, AdminMandatoryTask, \
    AdminBroadcastSG, AdminActiveTournamentsSG, GiveawaySG, AddAdminSG, AddTicketsSG
from rules.states import RulesSG
from shop.states import ShopSG
from start.states import StartSG, MenuSG, ProfileSG, UserGiveawaySG
from tournament.states import TournamentSG


async def switch_to_main_menu(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.done()
    await dialog_manager.start(state=MenuSG.menu)


async def switch_to_rules(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.done()
    await dialog_manager.start(state=RulesSG.start)


async def switch_to_ad(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.done()
    await dialog_manager.start(state=AdSG.start)


async def switch_to_admin_main(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.done()
    await dialog_manager.start(state=AdminMainSG.start)


async def switch_to_admin_statistic(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.done()
    await dialog_manager.start(state=AdminStatistic.start)


async def switch_to_admin_create_tournament(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.done()
    await dialog_manager.start(state=AdminCreateTournament.type)


async def switch_to_admin_ref_link(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.done()
    await dialog_manager.start(state=AdminRefLink.start)


async def switch_to_add_admin(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.done()
    await dialog_manager.start(state=AddAdminSG.id)


async def switch_to_add_tickets(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.done()
    await dialog_manager.start(state=AddTicketsSG.id)


async def switch_to_shop(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.done()
    await dialog_manager.start(state=ShopSG.start)


async def switch_to_tournaments(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.done()
    await dialog_manager.start(state=TournamentSG.start)


async def switch_to_my_tournaments(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.done()
    await dialog_manager.start(state=TournamentSG.my_tournaments)


async def switch_to_custom_tournaments(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.switch_to(state=TournamentSG.list_tournaments)
    dialog_manager.dialog_data['tournament_type'] = 'CUSTOM'


async def switch_to_tdm_tournaments(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.switch_to(state=TournamentSG.list_tournaments)
    dialog_manager.dialog_data['tournament_type'] = 'TDM'


async def switch_to_metro_tournaments(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.switch_to(state=TournamentSG.list_tournaments)
    dialog_manager.dialog_data['tournament_type'] = 'METRO'


async def switch_to_profile(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.done()
    await dialog_manager.start(state=ProfileSG.start)


async def switch_to_add_mandatory_task(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.done()
    await dialog_manager.start(state=AdminMandatoryTask.channel_id)


async def switch_to_broadcast(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.done()
    await dialog_manager.start(state=AdminBroadcastSG.photos)


async def switch_to_admin_active_tournaments(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.done()
    await dialog_manager.start(state=AdminActiveTournamentsSG.active_tournaments)


async def switch_to_admin_giveaway(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.done()
    await dialog_manager.start(state=GiveawaySG.name)


async def switch_to_giveaways(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.done()
    await dialog_manager.start(state=UserGiveawaySG.start)
