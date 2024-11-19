from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup, Select, Back, Row, ListGroup, Url, SwitchTo
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format

from start.getter import get_all_giveaways, get_user_giveaway_data
from start.handlers.correct import giveaway_selection
from start.saver import join_giveaway
from start.states import UserGiveawaySG
from utils.switcher import switch_to_main_menu

user_giveaway_dialog = Dialog(
    Window(
        Const('🎁 Розыгрыши', when='found'),
        ScrollingGroup(
            Select(
                Format('{item[name]}'),  # Используем ключ 'name'
                id='giveaways',
                item_id_getter=lambda x: x['id'],  # Используем ключ 'id' для получения item_id
                items='giveaways',
                on_click=giveaway_selection,
            ),
            width=1,
            id='giveaways_scrolling_group',
            height=6,
            when='found'
        ),
        Const('Розыгрыши не найдены', when='not_found'),
        Button(Const('🔙Назад'), id='tournaments_back', on_click=switch_to_main_menu),
        getter=get_all_giveaways,
        state=UserGiveawaySG.start,
    ),

    Window(
        Format("{text}"),
        DynamicMedia("photo", when='is_photo'),
        Const('Вы не подписаны на эти каналы.', when='not_subscribe'),
        ListGroup(
            Url(
                Format('{item[name]}'),
                Format('{item[url]}'),
                id='url'
            ),
            id='channels_list_group',
            item_id_getter=lambda item: item["name"],
            items='channels',
            when='not_subscribe'
        ),
        SwitchTo(Const('Я подписался👍'), id='i_subscribe', state=UserGiveawaySG.giveaway_info, when='not_subscribe'),
        Button(Const('✔ Участвовать'), id='enter_btn', when='subscribed', on_click=join_giveaway),
        Back(Const('🔙 Назад'), id='back_btn'),
        getter=get_user_giveaway_data,
        state=UserGiveawaySG.giveaway_info,
    )
)
