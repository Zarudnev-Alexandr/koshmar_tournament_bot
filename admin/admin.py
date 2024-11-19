from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import Button, Row, SwitchTo, Next, Column, Radio, ScrollingGroup, Select, Back
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format, Jinja

from admin.getter import get_admins_statistic, type_id_getter, TYPE_KEY, get_tournaments_types, get_ref_info, \
    get_admin_broadcast, send_broadcast, get_all_active_tournaments, start_tournament, tournament_members_getter, \
    get_tournament_members, get_winner_info, confirm_winner, delete_tournament, END_TYPE_KEY, get_end_types, \
    get_ref_links
from admin.handlers.check import photo_check, photos_check, skip_input_btn
from admin.handlers.correct import next_or_end, tournament_enter_result_getter, mandatory_task_enter_result_getter, \
    next_or_end_mandatory_task, next_or_end_admin_broadcast, tournament_selection, participant_selection, \
    next_or_end_admin_giveaway, on_sponsors_entered, get_giveaway_data, next_or_end_add_admin, get_added_admin, \
    next_or_end_add_ticckets, get_added_tickets, ref_link_selection, next_or_end_add_ref_link, \
    ref_link_enter_result_getter
from admin.handlers.error import CANCEL_EDIT, MY_NEXT, CANCEL_EDIT_mandatory_task, CANCEL_EDIT_admin_broadcast, \
    CANCEL_EDIT_admin_giveaway, NEXT_admin_giveaway, CANCEL_EDIT_add_admin, CANCEL_EDIT_add_tickets, \
    CANCEL_EDIT_add_ref_link
from admin.saver import save_tournament, save_mandatory_task, save_giveaway, save_added_admin, save_added_tickets, \
    save_ref_link
from admin.states import AdminMainSG, AdminStatistic, AdminCreateTournament, AdminRefLink, AdminMandatoryTask, \
    AdminBroadcastSG, AdminActiveTournamentsSG, GiveawaySG, AddAdminSG, AddTicketsSG
from tournament.getter import get_tournament_info
from utils.switcher import switch_to_admin_main, switch_to_admin_statistic, switch_to_main_menu, \
    switch_to_admin_create_tournament, switch_to_admin_ref_link, switch_to_add_mandatory_task, switch_to_broadcast, \
    switch_to_admin_active_tournaments, switch_to_admin_giveaway, switch_to_add_admin, switch_to_add_tickets

admin_main_dialog = Dialog(
    Window(
        Const('Это админ панель'),
        Button(Const('📈 Статистика'), id='stat_btn', on_click=switch_to_admin_statistic),
        Button(Const('📧 Создание рассылок'), id='messages_btn', on_click=switch_to_broadcast),
        Button(Const('🎁 Создание розыгрышей на тикеты'), id='presents_btn', on_click=switch_to_admin_giveaway),
        Button(Const('🥊 Создание турниров'), id='tournaments_btn', on_click=switch_to_admin_create_tournament),
        Button(Const('➕ Добавить админа'), id='admin_add_btn', on_click=switch_to_add_admin),
        Button(Const('🔗 Реф ссылка'), id='ref_link_btn', on_click=switch_to_admin_ref_link),
        Button(Const('🔍 Активные турниры'), id='active_tournaments_btn', on_click=switch_to_admin_active_tournaments),
        Button(Const('👀 Добавить обязательное задание'), id='add_task_btn', on_click=switch_to_add_mandatory_task),
        Button(Const('🎫️ Добавить тикетов'), id='add_tickets_btn', on_click=switch_to_add_tickets),
        Button(Const('🔙 Назад'), id='ad_btn', on_click=switch_to_main_menu),
        state=AdminMainSG.start
    ),
)

admin_statistics_dialog = Dialog(
    Window(
        Const('📈 Статистика:\n'),
        Format('📃 Выполнивших обязательные задания: {completed_tasks}\n'
               '👩‍💻 Всего пользователей: {total_users}\n'
               '⌛ Новых пользователей в день: {new_users_today}'),
        Button(Const('🔙 Назад'), id='ad_btn', on_click=switch_to_admin_main),
        getter=get_admins_statistic,
        state=AdminStatistic.start
    )
)

admin_create_tournaments_dialog = Dialog(
    Window(
        Const("Тип турнира:"),
        Column(
            Radio(
                checked_text=Format("🔘 {item.emoji} {item.name}"),
                unchecked_text=Format("⚪️ {item.emoji} {item.name}"),
                id="tournament_type",
                items=TYPE_KEY,
                item_id_getter=type_id_getter,
            ),
        ),
        MY_NEXT,
        CANCEL_EDIT,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=AdminCreateTournament.type,
        getter=get_tournaments_types,
    ),

    Window(
        Const(text='Обложка турнира:'),
        MessageInput(
            func=photo_check,
            content_types=ContentType.PHOTO,
        ),
        CANCEL_EDIT,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=AdminCreateTournament.photo,
    ),

    Window(
        Const('Название турнира:'),
        TextInput(
            id="name",
            type_factory=str,
            on_success=next_or_end,
        ),
        CANCEL_EDIT,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=AdminCreateTournament.name,
    ),

    Window(
        Const('Цена в тикетах:'),
        TextInput(
            id="price",
            type_factory=int,
            on_success=next_or_end,
        ),
        CANCEL_EDIT,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=AdminCreateTournament.price,
    ),

    Window(
        Const('Количество мест:'),
        TextInput(
            id="number_of_players",
            type_factory=int,
            on_success=next_or_end,
        ),
        CANCEL_EDIT,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=AdminCreateTournament.number_of_players,
    ),

    Window(
        Const('Награда за первое место (любой текст): '),
        TextInput(
            id="first_place_award",
            type_factory=str,
            on_success=next_or_end,
        ),
        CANCEL_EDIT,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=AdminCreateTournament.first_place_award,
    ),

    Window(
        Const('Описание (любой текст): '),
        TextInput(
            id="description",
            type_factory=str,
            on_success=next_or_end,
        ),
        CANCEL_EDIT,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=AdminCreateTournament.description,
    ),

    Window(
        Const('Ссылка на группу: '),
        TextInput(
            id="link",
            type_factory=str,
            on_success=next_or_end,
        ),
        CANCEL_EDIT,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=AdminCreateTournament.link,
    ),

    Window(
        Const('ID группы: '),
        TextInput(
            id="group_id",
            type_factory=str,
            on_success=next_or_end,
        ),
        CANCEL_EDIT,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=AdminCreateTournament.group_id,
    ),

    Window(
        DynamicMedia("photo"),
        Jinja(
            "<u>Проверка введенных данных турнира:</u>\n\n"
            "<b>Тип</b>: {{type.icon}} {{type.title}}\n"
            "<b>Название</b>: {{name}}\n"
            "<b>Цена в тикетах</b>: {{price}}\n"
            "<b>Количество мест</b>: {{number_of_players}}\n"
            "<b>Награда за первое место</b>: {{first_place_award}}\n"
            "<b>Описание</b>: {{description}}\n"
            "<b>Ссылка на группу</b>: {{link}}\n"
            "<b>ID группы</b>: {{group_id}}\n"
        ),
        Row(
            SwitchTo(Const("Изменить тип"), state=AdminCreateTournament.type, id="edit_type"),
            SwitchTo(Const("Изменить название"), state=AdminCreateTournament.name, id="edit_name"),
        ),
        Row(
            SwitchTo(Const("Изменить цену"), state=AdminCreateTournament.price, id="edit_price"),
            SwitchTo(Const("Изменить количество мест"), state=AdminCreateTournament.number_of_players,
                     id="edit_number_of_players"),
        ),
        Row(
            SwitchTo(Const("Изменить награду"), state=AdminCreateTournament.first_place_award,
                     id="edit_first_place_award"),
            SwitchTo(Const("Изменить описание"), state=AdminCreateTournament.description, id="edit_description"),
        ),
        Row(
            SwitchTo(Const("Изменить ссылку на группу"), state=AdminCreateTournament.link, id="edit_link"),
            SwitchTo(Const("Изменить ID группы"), state=AdminCreateTournament.group_id, id="edit_group_id"),
        ),
        Row(

            SwitchTo(Const("Изменить обложку"), state=AdminCreateTournament.photo, id="edit_photo"),
        ),
        Row(
            Next(Const('Сохранить✅'), id='button_save'),
            Button(Const("Отмена❌"), id="button_cancel", on_click=switch_to_admin_main),
        ),
        state=AdminCreateTournament.preview,
        getter=tournament_enter_result_getter,
        parse_mode="html",
    ),

    Window(
        DynamicMedia("photo"),
        Format(
            text=(
                '✅ Вы успешно создали турнир!\n\n'
                '📌 <b>Тип:</b> {tournament_type}\n'
                '📛 <b>Название:</b> {name}\n'
                '🎫️ <b>Цена участия:</b> {price_in_tickets} билетов\n'
                '👥 <b>Количество слотов:</b> {total_slots}\n'
                '🏆 <b>Приз за 1 место:</b> {reward_first_place}\n'
                '📄 <b>Описание:</b> {description}\n'
                '🔗 <b>Ссылка на группу:</b> {group_link}\n'
                '🆔 <b>ID группы:</b> {group_id}'
            )
        ),
        Button(Const('📃В админ меню'), id='to_admin_menu', on_click=switch_to_admin_main),
        getter=save_tournament,
        state=AdminCreateTournament.save
    )
)

# admin_ref_link_dialog = Dialog(
#     Window(
#         Const('🔗 Ваша реферальная ссылка:\n'),
#         Format('<code>{ref_link}</code>\n'),
#         Format('® По ссылке зарегистрировалось: {count_ref_registered}'),
#         Format('👀 А вот, сколько из них выполнили задания: {count_watch_ad}'),
#         Button(Const('🔙 Назад'), id='back_btn', on_click=switch_to_admin_main),
#         getter=get_ref_info,
#         state=AdminRefLink.start
#     )
# )


admin_ref_link_dialog = Dialog(
    Window(
        Const("Выбери название реферальной ссылки:"),
        ScrollingGroup(
            Select(
                Format('{item[link_name]}'),
                id='ref_link',
                item_id_getter=lambda x: x["link_user_id"],
                items='ref_links',
                on_click=ref_link_selection,
            ),
            width=1,
            id='ref_links_scrolling_group',
            height=6,
            when='found'
        ),
        Const('Реферальные ссылки не найдены.', when='not_found'),
        SwitchTo(Const('Добавить ссылку'), id='switch_to_input_name', state=AdminRefLink.input_name),
        Button(Const('🔙 Назад'), id='back_btn', on_click=switch_to_admin_main),
        getter=get_ref_links,
        state=AdminRefLink.start
    ),

    Window(
        Const('🔗 Ваша реферальная ссылка:\n'),
        Format('Название ссылки: {org_name}\n'),
        Format('<code>{ref_link}</code>\n'),
        Format('® По ссылке зарегистрировалось: {count_ref_registered}'),
        Format('👀 А вот, сколько из них выполнили задания: {count_watch_ad}'),
        Back(Const('🔙 Назад'), id='back_btn'),
        getter=get_ref_info,
        state=AdminRefLink.info
    ),

    Window(
        Const('Название ссылки:'),
        TextInput(
            id="link_name",
            type_factory=str,
            on_success=next_or_end_add_ref_link,
        ),
        CANCEL_EDIT_add_ref_link,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=AdminRefLink.input_name,
    ),

    Window(
        Jinja(
            "<u>Проверка введенных данных реф ссылки:</u>\n\n"
            "<b>Название ссылки</b>: {{link_name}}\n"
        ),
        Row(
            Next(Const('Сохранить✅'), id='button_save'),
            Button(Const("Отмена❌"), id="button_cancel", on_click=switch_to_admin_main),
        ),
        state=AdminRefLink.preview,
        getter=ref_link_enter_result_getter,
        parse_mode="html",
    ),

    Window(
        Format(
            text=(
                '✅ Вы успешно создали реферальную ссылку!\n\n'
                '📛 <b>Название:</b> {org_name}\n'
                '🔗 <b>Ссылка:</b> {ref_link}'
            )
        ),
        Button(Const('📃В админ меню'), id='to_admin_menu', on_click=switch_to_admin_main),
        getter=save_ref_link,
        state=AdminRefLink.save
    )
)

admin_create_mandatory_task_dialog = Dialog(
    Window(
        Const('ID канала:'),
        TextInput(
            id="channel_id",
            type_factory=int,
            on_success=next_or_end_mandatory_task,
        ),
        CANCEL_EDIT_mandatory_task,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=AdminMandatoryTask.channel_id,
    ),

    Window(
        Const('Ссылка на канал:'),
        TextInput(
            id="channel_link",
            type_factory=str,
            on_success=next_or_end_mandatory_task,
        ),
        CANCEL_EDIT_mandatory_task,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=AdminMandatoryTask.channel_link,
    ),
    Window(
        Jinja(
            "<u>Проверка введенных данных канала:</u>\n\n"
            "<b>ID канала</b>: {{channel_id}}\n"
            "<b>Ссылка</b>: {{channel_link}}\n"
            "<b>Название канала</b>: {{channel_name}}\n"
        ),
        Row(
            SwitchTo(Const("Изменить ID группы"), state=AdminMandatoryTask.channel_id, id="edit_channel_id"),
            SwitchTo(Const("Изменить ссылку на группу"), state=AdminMandatoryTask.channel_link, id="edit_channel_link"),
        ),
        Row(
            Next(Const('Сохранить✅'), id='button_save'),
            Button(Const("Отмена❌"), id="button_cancel", on_click=switch_to_admin_main),
        ),
        state=AdminMandatoryTask.preview,
        getter=mandatory_task_enter_result_getter,
        parse_mode="html",
    ),

    Window(
        Format(
            text=(
                '✅ Вы успешно создали задание на подписку!\n\n'
                '📛 <b>Название:</b> {channel_name}\n'
                '🔗 <b>Ссылка на группу:</b> {channel_link}\n'
                '🆔 <b>ID группы:</b> {channel_id}'
            )
        ),
        Button(Const('📃В админ меню'), id='to_admin_menu', on_click=switch_to_admin_main),
        getter=save_mandatory_task,
        state=AdminMandatoryTask.save
    )
)

# Создание рассылки
admin_broadcast_create_dialog = Dialog(
    Window(
        Const(text='Фото для рассылки:'),
        MessageInput(
            func=photos_check,
            content_types=[ContentType.PHOTO],
        ),
        Button(Const("Перейти к тексту ➡"), id="next", on_click=lambda c, b, d: d.next()),
        CANCEL_EDIT_admin_broadcast,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=AdminBroadcastSG.photos,
    ),

    Window(
        Const("Текст для рассылки:"),
        TextInput(id="broadcast_text",
                  type_factory=str,
                  on_success=next_or_end_admin_broadcast),
        CANCEL_EDIT_admin_broadcast,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=AdminBroadcastSG.text
    ),

    Window(
        Const("Текст для кнопки:"),
        TextInput(id="button_text",
                  type_factory=str,
                  on_success=next_or_end_admin_broadcast),
        CANCEL_EDIT_admin_broadcast,
        Button(Const('Без кнопок ▶'), id='next1', on_click=skip_input_btn),
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=AdminBroadcastSG.button_text
    ),

    Window(
        Const("Ссылка для кнопки:"),
        TextInput(id="button_link",
                  type_factory=str,
                  on_success=next_or_end_admin_broadcast),
        CANCEL_EDIT_admin_broadcast,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=AdminBroadcastSG.button_link
    ),

    Window(
        Const("Предпросмотр рассылки:"),
        Jinja(
            "Текст: {{ broadcast_text }}\n"
            "{% if button_text and button_link %}Кнопка: {{ button_text }}\nСсылка: {{ button_link }}{% endif %}"
        ),
        Row(
            Button(Const('Начать рассылку✅'), id='button_save', on_click=send_broadcast),
            Button(Const("Отмена❌"), id="button_cancel", on_click=switch_to_admin_main),
        ),
        getter=get_admin_broadcast,
        state=AdminBroadcastSG.preview
    )
)

# выбираем победителя турнира
admin_active_tournaments_dialog = Dialog(
    Window(
        Const("Список активных турниров:", when='found'),
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
        Button(Const('🔙 Назад'), id='back_btn', on_click=switch_to_admin_main),
        getter=get_all_active_tournaments,
        state=AdminActiveTournamentsSG.active_tournaments
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
                '📄 <b>Описание:</b> {description}\n\n'
                '❓ <b>Статус:</b>{status}'
            )
        ),
        Row(
            Button(Const('🎬 Задать статус "Начато"'), id='start_tournament_btn', on_click=start_tournament,
                   when='is_not_started'),
            SwitchTo(Const('👑 Выбрать победителя'), id='select_winner_btn',
                     state=AdminActiveTournamentsSG.select_winner, when='lets_sum_it_up'),
        ),
        Row(
            Button(Const('❌ Удалить турнир'), id='delete_tournament_btn', on_click=delete_tournament)
        ),
        Row(
            SwitchTo(Const('🔙Назад'), id='tournaments_back', state=AdminActiveTournamentsSG.active_tournaments),
            Button(Const('📃В главное меню'), id='to_main_menu', on_click=switch_to_main_menu),
            Next(Const('Участники'))
        ),

        getter=get_tournament_info,
        state=AdminActiveTournamentsSG.tournament_info
    ),

    Window(
        Format("Список участников турнира:\n\n{members_list}", when='found'),
        Format("Участников нет😥", when='not_found'),
        Back(Const('Назад')),
        getter=tournament_members_getter,
        state=AdminActiveTournamentsSG.get_members
    ),

    Window(
        Const("Выбери участника для отображения информации:"),
        ScrollingGroup(
            Select(
                Format('{item[pubg_id]}'),
                id='participant',
                item_id_getter=lambda x: x["tg_id"],
                items='participants',
                on_click=participant_selection,
            ),
            width=2,
            id='participants_scrolling_group',
            height=6,
            when='found'
        ),
        Const('Участники не найдены для данного турнира.', when='not_found'),
        Button(Const('🔙 Назад'), id='back_btn', on_click=switch_to_admin_main),
        getter=get_tournament_members,
        state=AdminActiveTournamentsSG.select_winner
    ),

    Window(
        Format(
            text=(
                '<b>Username:</b> {username}\n'
                '<b>TG ID:</b> {tg_id}\n'
                '<b>PUBG ID:</b> {pubg_id}'
            )
        ),
        Row(
            Button(Const('👑 Он победил'), id='he_is_winner_btn', on_click=confirm_winner),
        ),
        Row(
            SwitchTo(Const('🔙Назад'), id='tournaments_back', state=AdminActiveTournamentsSG.active_tournaments),
            Button(Const('📃В главное меню'), id='to_main_menu', on_click=switch_to_main_menu),
        ),

        getter=get_winner_info,
        state=AdminActiveTournamentsSG.winner_info
    ),
)

# Диалог создания розыгрышей
giveaway_dialog = Dialog(
    Window(
        Const("Введите название розыгрыша:"),
        TextInput(id="name",
                  type_factory=str,
                  on_success=next_or_end_admin_giveaway),
        CANCEL_EDIT_admin_giveaway,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=GiveawaySG.name,
    ),

    Window(
        Const(text='Отправьте фото для розыгрыша (или нажмите "Пропустить"):'),
        MessageInput(
            func=photo_check,
            content_types=ContentType.PHOTO,
        ),
        Next(Const('Пропустить ▶')),
        CANCEL_EDIT_admin_giveaway,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=GiveawaySG.photo,
    ),

    Window(
        Const("Введите спонсоров в формате: (ссылка, id)\n"
              "Каждый спонсор с новой строки и в круглых скобках, например:\n"
              "(https://t.me/group1, -100123456789)\n"
              "(https://t.me/group2, -100987654321)"),
        MessageInput(func=on_sponsors_entered),
        CANCEL_EDIT_admin_giveaway,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=GiveawaySG.sponsors,
    ),

    Window(
        Const("Выберите тип окончания розыгрыша:"),
        Column(
            Radio(
                checked_text=Format("🔘 {item.emoji} {item.name}"),
                unchecked_text=Format("⚪️ {item.emoji} {item.name}"),
                id="end_type_radio",
                items=END_TYPE_KEY,
                item_id_getter=type_id_getter,
            ),
        ),
        NEXT_admin_giveaway,
        CANCEL_EDIT_admin_giveaway,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=GiveawaySG.end_type,
        getter=get_end_types,
    ),

    Window(
        Format('Введите фактор окончания турнира (если в прошлом окне вы выбрали "По времени", то введите '
               'количество часов, через которое розыгрыш завершится, а если вы выбрали "По количеству участников", '
               'то введите количество участников, '
               'при собрании которого, розыгрыш завершится):'),
        TextInput(id="end_value",
                  type_factory=str,
                  on_success=next_or_end_admin_giveaway),
        CANCEL_EDIT_admin_giveaway,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=GiveawaySG.end_value,
    ),
    Window(
        Const("Введите количество призовых мест:"),
        TextInput(id="prize_places",
                  type_factory=str,
                  on_success=next_or_end_admin_giveaway),
        CANCEL_EDIT_admin_giveaway,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=GiveawaySG.prize_places,
    ),
    Window(
        Const('Введите награды за каждое место в тикетах (через запятую). Вводите именно столько наград, '
              'сколько указали призовых мест! "Защита от дурака" не предусмотрена:'),
        TextInput(id="ticket_rewards",
                  type_factory=str,
                  on_success=next_or_end_admin_giveaway),
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=GiveawaySG.ticket_rewards,
    ),
    Window(
        Format("{text}"),
        DynamicMedia("photo", when='is_photo'),
        Button(Const("✅ Начать розыгрыш"), id="confirm", on_click=save_giveaway),
        Button(Const('🔙 Назад'), id='back_btn', on_click=switch_to_admin_main),
        getter=get_giveaway_data,
        state=GiveawaySG.preview,
    ),
)

# Добавление админа
add_admin_dialog = Dialog(
    Window(
        Const("Тг id новго админа:"),
        TextInput(id="admin_id_text",
                  type_factory=int,
                  on_success=next_or_end_add_admin),
        CANCEL_EDIT_add_admin,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=AddAdminSG.id
    ),

    Window(
        Jinja(
            'Вы хотите сделать админом его: \n'
            '🪪 TG ID: <code>{{tg_id}}</code>\n'
            '🆔 PUBG ID: <code>{{pubg_id}}</code>\n',
            when='found'
        ),
        Const('пользователь с таким тг id не найден!', when='not_found'),
        Row(
            Next(Const('Назначить админом ✅'), id='button_save', when='found'),
            Button(Const("Отмена ❌"), id="button_cancel", on_click=switch_to_admin_main),
        ),
        getter=get_added_admin,
        state=AddAdminSG.preview
    ),

    Window(
        Format(
            text=(
                '✅ Вы успешно добавили пользователя с ID {tg_id} в качестве админа'
            )
        ),
        Button(Const('📃В админ меню'), id='to_admin_menu', on_click=switch_to_admin_main),
        getter=save_added_admin,
        state=AddAdminSG.save
    )
)

# Добавление тикетов
add_tickets_dialog = Dialog(
    Window(
        Const("Тг id пользователя, которому нужно пополнить баланс:"),
        TextInput(id="user_id",
                  type_factory=int,
                  on_success=next_or_end_add_ticckets),
        CANCEL_EDIT_add_tickets,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=AddTicketsSG.id
    ),

    Window(
        Const("Сколько тикетов добавляем:"),
        TextInput(id="tickets_count",
                  type_factory=int,
                  on_success=next_or_end_add_ticckets),
        CANCEL_EDIT_add_tickets,
        Button(Const('❌ Отмена'), id='cancel', on_click=switch_to_admin_main),
        state=AddTicketsSG.count
    ),

    Window(
        Jinja(
            'Вы хотите добавить тикетов: \n'
            '🪪 TG ID пользователя: <code>{{user_id}}</code>\n'
            '🎫️ Количество тикетов: {{tickets_count}}\n',
            when='found'
        ),
        Const('пользователь с таким тг id не найден!', when='not_found'),
        Row(
            Next(Const('Начислить ✅'), id='button_save', when='found'),
            Button(Const("Отмена ❌"), id="button_cancel", on_click=switch_to_admin_main),
        ),
        getter=get_added_tickets,
        state=AddTicketsSG.preview
    ),

    Window(
        Format(
            text=(
                '✅ Вы успешно добавили {tickets_count} пользователю с ID {user_id}'
            )
        ),
        Button(Const('📃В админ меню'), id='to_admin_menu', on_click=switch_to_admin_main),
        getter=save_added_tickets,
        state=AddTicketsSG.save
    )
)
