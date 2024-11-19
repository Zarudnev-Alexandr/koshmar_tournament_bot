from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const

from rules.states import RulesSG
from utils.switcher import switch_to_main_menu

subscribe_dialog = Dialog(
    Window(
        StaticMedia(
            url="https://drive.google.com/uc?export=view&id=1CmO6mOjBoH3uBDTxGUGoUCwRZbe3mHl5",
        ),
        Const('<b>Добро пожаловать в бота Турниры от КОШМАРА!</b>\n\n'
              'Уважаемые участники и гости! Мы рады приветствовать вас в нашем боте. '
              'Чтобы мероприятии прошли успешно, честно и безопасно, ознакомьтесь с '
              'основными правилами участия и поведения на турнирах.\n\n'
              '<a href="https://t.me/koshmrRULES" style="color: blue;">t.me/koshmrRULES</a>'),

        # Кнопки
        Button(Const('🔙 Назад'), id='to_main_menu', on_click=switch_to_main_menu),

        # Остальное
        state=RulesSG.start,
    )
)
