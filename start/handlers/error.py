from typing import Any

from aiogram import F
from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const

from start.handlers.correct import FINISHED_KEY
from start.states import RegistrationSG


async def no_text(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    await message.answer(text='Вы ввели что-то, совсем не похожее на текст')


async def pubg_id_error(message: Message, dialog_: Any, manager: DialogManager, error_: ValueError):
    await message.answer("Неверный формат PUBG ID. Убедитесь, что он начинается с '51' и имеет от 8 до 12 цифр.")


CANCEL_EDIT = SwitchTo(
    Const("Отменить редактирование"),
    when=F["dialog_data"][FINISHED_KEY],
    id="cnl_edt",
    state=RegistrationSG.preview,
)
