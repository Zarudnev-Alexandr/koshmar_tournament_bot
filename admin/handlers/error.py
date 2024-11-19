from aiogram import F
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const

from admin.handlers.correct import FINISHED_KEY
from admin.states import AdminCreateTournament, AdminMandatoryTask, AdminBroadcastSG, GiveawaySG, AddAdminSG, \
    AddTicketsSG, AdminRefLink

CANCEL_EDIT = SwitchTo(
    Const("Отменить редактирование"),
    when=F["dialog_data"][FINISHED_KEY],
    id="cnl_edt",
    state=AdminCreateTournament.preview,
)


CANCEL_EDIT_mandatory_task = SwitchTo(
    Const("Отменить редактирование"),
    when=F["dialog_data"][FINISHED_KEY],
    id="cnl_edt",
    state=AdminMandatoryTask.preview,
)

CANCEL_EDIT_admin_broadcast = SwitchTo(
    Const("Отменить редактирование"),
    when=F["dialog_data"][FINISHED_KEY],
    id="cnl_edt",
    state=AdminBroadcastSG.preview,
)


CANCEL_EDIT_add_admin = SwitchTo(
    Const("Отменить редактирование"),
    when=F["dialog_data"][FINISHED_KEY],
    id="cnl_edt",
    state=AddAdminSG.preview,
)


CANCEL_EDIT_add_tickets = SwitchTo(
    Const("Отменить редактирование"),
    when=F["dialog_data"][FINISHED_KEY],
    id="cnl_edt",
    state=AddTicketsSG.preview,
)


CANCEL_EDIT_admin_giveaway = SwitchTo(
    Const("Отменить редактирование"),
    when=F["dialog_data"][FINISHED_KEY],
    id="cnl_edt",
    state=GiveawaySG.preview,
)


CANCEL_EDIT_add_ref_link = SwitchTo(
    Const("Отменить редактирование"),
    when=F["dialog_data"][FINISHED_KEY],
    id="cnl_edt",
    state=AdminRefLink.preview,
)

MY_NEXT = SwitchTo(
    Const("Подтвердить"),
    when=~F["dialog_data"][FINISHED_KEY],
    id="nxt",
    state=AdminCreateTournament.photo,
)


NEXT_admin_giveaway = SwitchTo(
    Const("Подтвердить"),
    when=~F["dialog_data"][FINISHED_KEY],
    id="nxt",
    state=GiveawaySG.end_value,
)