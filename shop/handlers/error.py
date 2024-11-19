from aiogram import F
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const

from shop.handlers.correct import FINISHED_KEY
from start.states import RegistrationSG

CANCEL_EDIT = SwitchTo(
    Const("Отменить редактирование"),
    when=F["dialog_data"][FINISHED_KEY],
    id="cnl_edt",
    state=RegistrationSG.preview,
)