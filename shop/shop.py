from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Next, Row, Button, SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja

from shop.handlers.correct import next_or_end, shop_enter_result_getter, shop_enter_success, buy_tickets
from shop.handlers.error import CANCEL_EDIT
from shop.states import ShopSG
from utils.switcher import switch_to_main_menu

shop_dialog = Dialog(
    Window(
        Const("💸 Приветствуем вас в магазине. Здесь вы можете приобрести тикеты для участия на турнирах.\n"
              "💹 Текущий курс тикетов: 15 ⭐ = 1 🎫\n"
              "⭐ - [Звезды телеграмм ](https://telegram.org/blog/telegram-stars/ru)\n"
              "✨ Для того чтобы приобрести, нажмите кнопку ниже:"),
        Next(Const('⭐ Купить')),
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_main_menu),
        state=ShopSG.start
    ),

    Window(
        Const(text='Сколько тикетов вы хотите купить?'),
        TextInput(
            id="tickets_count",
            type_factory=int,
            on_success=shop_enter_success,
        ),
        CANCEL_EDIT,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_main_menu),
        state=ShopSG.buy_tickets
    ),

    Window(
        Jinja(
            "<u>Подтверждение покупки:</u>\n\n"
            "<b>Количество тикетов</b>: {{tickets_count}}\n"
        ),

        Row(
            SwitchTo(Const("Изменить количество покупаемых тикетов"), state=ShopSG.buy_tickets, id="edit_count"),
        ),
        Row(
            Button(Const('Купить ✅'), id='button_save', on_click=buy_tickets),
            Button(Const("Отмена ❌"), id="button_cancel", on_click=switch_to_main_menu),
        ),
        state=ShopSG.preview,
        getter=shop_enter_result_getter,
        parse_mode="html",
    ),
)
