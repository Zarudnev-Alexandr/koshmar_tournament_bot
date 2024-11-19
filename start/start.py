from aiogram import Router
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Row, Button, Next, SwitchTo, ListGroup, Url
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Format, Const, Jinja

from start.getter import get_user_when_entered, get_menu
from start.handlers.correct import pubg_id_success, result_getter
from start.handlers.error import pubg_id_error, CANCEL_EDIT
from start.saver import save_user
from start.states import RegistrationSG, MenuSG
from utils.switcher import switch_to_rules, switch_to_ad, switch_to_main_menu, switch_to_admin_main, switch_to_shop, \
    switch_to_tournaments, switch_to_profile, switch_to_giveaways

start_router = Router()

start_dialog = Dialog(
    Window(
        Const('👋 Здравствуйте! Добро пожаловать в турнирного бота от Кошмара.\n'
              'Необходимо зарегистрироваться', when='new_user'),
        Const('👋 Здравствуйте! Добро пожаловать в турнирного бота от Кошмара.', when='old_user'),
        SwitchTo(
            Const("Регистрация"),
            id="registration",
            state=RegistrationSG.pubg_id,
            when='new_user'
        ),
        Button(Const('📃В главное меню'), id='to_main_menu', on_click=switch_to_main_menu, when='old_user'),
        state=RegistrationSG.start,
        getter=get_user_when_entered,
    ),
    Window(
        Const('🆔 Для начало, вам необходимо привязать ваш PUBG MOBILE ID. Укажите его ниже 👇.\n'
              '⚠️ Указывайте PUBG MOBILE ID корректно! В случае если вы указали не правильно, вы можете сменить его '
              'только один раз, обратившись к @koshmr2kd.'),
        TextInput(
            id="pubg_id",
            type_factory=int,
            on_error=pubg_id_error,
            on_success=pubg_id_success,
        ),
        CANCEL_EDIT,
        state=RegistrationSG.pubg_id,
    ),
    Window(
        Jinja(
            "<u>Вы ввели</u>:\n\n"
            "<b>Pubg id</b>: {{pubg_id}}\n",
        ),
        SwitchTo(
            Const("Изменить Pubg id"),
            state=RegistrationSG.pubg_id, id="to_pubg_id",
        ),
        Next(Const('Сохранить✅'), id='button_save'),
        state=RegistrationSG.preview,
        getter=result_getter,
        parse_mode="html",
    ),
    Window(
        Format(text='✅ Вы успешно привязали: <b>{pubg_id}</b> к своему профилю телеграмм. '
                    'Теперь вам доступны все функции бота.\n'),
        Button(Const('📃В главное меню'), id='to_main_menu', on_click=switch_to_main_menu),
        getter=save_user,
        state=RegistrationSG.save
    ),
)

menu_dialog = Dialog(
    Window(
        Const(text='Вы не подписаны на эти каналы.', when='not_subscribe'),
        ListGroup(
            Url(
                Format('{item[name]}'),
                Format('{item[url]}'),
                id='url'
            ),
            id='channels_list_group',
            item_id_getter=lambda item: item["id"],
            items='channels',
            when='not_subscribe'
        ),
        SwitchTo(Const('Я подписался👍'), id='i_subscribe', state=MenuSG.menu, when='not_subscribe'),

        StaticMedia(
            url="https://drive.google.com/uc?export=view&id=1NYi-kulcO8HA_nIJa6hOUvQrDqZKzONG",
            when="subscribe"
        ),
        Format('Меню', when='subscribe'),
        Row(
            Button(Const('👤 Профиль'), id='profile_btn', on_click=switch_to_profile),
            Button(Const('💸 Купить тикет'), id='buy_ticket_btn', on_click=switch_to_shop),
            when='subscribe'
        ),
        Row(
            Button(Const('⚔️Турниры'), id='tournaments_btn', on_click=switch_to_tournaments),
            Button(Const('🎁 Розыгрыши'), id='draws_btn', on_click=switch_to_giveaways),
            when='subscribe'
        ),
        Row(
            Button(Const('❓ Информация / Правила'), id='rules_btn', on_click=switch_to_rules),
            when='subscribe'
        ),
        Row(
            Button(Const('✨ Халява от Кошмара'), id='ad_btn', on_click=switch_to_ad),
            when='subscribe'
        ),
        Row(
            Button(Const('Админ панель'), id='admin_btn', on_click=switch_to_admin_main, when='admin_user'),
        ),

        getter=get_menu,
        state=MenuSG.menu
    )
)
