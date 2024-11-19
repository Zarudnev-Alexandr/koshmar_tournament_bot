from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup, Select, Back, SwitchTo, Row
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format

from tournament.getter import get_all_tournaments, get_tournament_info, check_tournament_enter, get_my_tournaments
from tournament.handlers.correct import tournament_selection
from tournament.states import TournamentSG
from utils.switcher import switch_to_my_tournaments, switch_to_custom_tournaments, switch_to_tdm_tournaments, \
    switch_to_metro_tournaments, switch_to_admin_main, switch_to_main_menu

tournament_dialog = Dialog(
    Window(
        Const('⚔️ Выберите категорию турниров:'),
        Button(Const('👤 Мои турниры'), id='my_tournaments_btn', on_click=switch_to_my_tournaments),
        Button(Const('🪓 Кастомки'), id='custom_btn', on_click=switch_to_custom_tournaments),
        Button(Const('🗡️ ТДМ турниры'), id='tdm_btn', on_click=switch_to_tdm_tournaments),
        Button(Const('🔪 Метро турниры'), id='metro_btn', on_click=switch_to_metro_tournaments),
        Button(Const('🔙Назад'), id='tournaments_back', on_click=switch_to_main_menu),
        state=TournamentSG.start
    ),

    Window(
        Const('Выбери турнир:', when='found'),
        ScrollingGroup(
            Select(
                Format('{item[0]}'),
                id='tournament',
                item_id_getter=lambda x: x[1],
                items='tournaments',
                on_click=tournament_selection,
            ),
            width=1,
            id='tournaments_scrolling_group',
            height=6,
            when='found'
        ),
        Const('Турниры не найдены', when='not_found'),
        SwitchTo(Const('🔙Назад'), id='tournaments_back', state=TournamentSG.start),
        getter=get_my_tournaments,
        state=TournamentSG.my_tournaments
    ),

    Window(
        DynamicMedia("photo"),
        Format(
            text=(
                '<b>{name}</b>\n\n'
                '{tournament_type}\n'
                '🎫️ <b>Цена:</b> {price_in_tickets}\n'
                '👥 <b>Мест:</b> {current_participants}/{total_slots}\n'
                '🏆 <b>Приз за первое место:</b> {reward_first_place}\n'
                '📄 <b>Описание:</b> {description}\n'
                '❓ <b>Статус:</b>{status}\n\n'
                '<i>👑 За выигранный турнир вы получите потраченные тикеты обратно!</i>\n'
            )
        ),
        Row(
            SwitchTo(Const('🔙Назад'), id='tournaments_back', state=TournamentSG.my_tournaments),
            Button(Const('📃В главное меню'), id='to_main_menu', on_click=switch_to_main_menu),
        ),

        getter=get_tournament_info,
        state=TournamentSG.my_tournament_info
    ),

    Window(
        Const('Выбери турнир:', when='found'),
        ScrollingGroup(
            Select(
                Format('{item[0]}'),
                id='tournament',
                item_id_getter=lambda x: x[1],
                items='tournaments',
                on_click=tournament_selection,
            ),
            width=1,
            id='tournaments_scrolling_group',
            height=6,
            when='found'
        ),
        Const('Турниры не найдены', when='not_found'),
        SwitchTo(Const('🔙Назад'), id='tournaments_back', state=TournamentSG.start),
        getter=get_all_tournaments,
        state=TournamentSG.list_tournaments
    ),

    Window(
        DynamicMedia("photo"),
        Format(
            text=(
                '<b>{name}</b>\n\n'
                '{tournament_type}\n'
                '🎫️ <b>Цена:</b> {price_in_tickets}\n'
                '👥 <b>Мест:</b> {current_participants}/{total_slots}\n'
                '🏆 <b>Приз за первое место:</b> {reward_first_place}\n'
                '📄 <b>Описание:</b> {description}\n'
                '❓ <b>Статус:</b>{status}\n\n'
                '<i>👑 За выигранный турнир вы получите потраченные тикеты обратно!</i>\n'
            )
        ),
        Row(
            Button(Const('🎫 Войти'), id='enter_tournament_btn', on_click=check_tournament_enter, when='is_not_full'),
            when='is_not_started'
        ),
        Row(
            SwitchTo(Const('🔙Назад'), id='tournaments_back', state=TournamentSG.start),
            Button(Const('📃В главное меню'), id='to_main_menu', on_click=switch_to_main_menu),
        ),

        getter=get_tournament_info,
        state=TournamentSG.tournament_info
    )
)
