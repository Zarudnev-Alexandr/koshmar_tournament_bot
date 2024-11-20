from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format

from start.getter import get_profile
from start.states import ProfileSG
from utils.switcher import switch_to_main_menu

profile_dialog = Dialog(
    Window(
        StaticMedia(
            url="https://drive.google.com/uc?export=view&id=1Ju9xhA6gt03ByeiXagn_Ixa5kB2WmtTt",
        ),
        Const('👤 Ваш профиль:'),
        Format(
            text=(
                '🪪 TG ID: <code>{tg_id}</code>\n'
                '🆔 PUBG ID: <code>{pubg_id}</code>\n'
                '🎫 Тикетов: {tickets}\n\n'
                '👥 Рефералы: \n'
                '🔗 Ваша реферальная ссылка: <code>{referral_link}</code>\n'
                '🫂 Приглашено рефералов: {referrals_count}\n'
                '🎟️ Заработали с рефералов: ❓\n\n'
                '📊 Статистика: \n'
                '🎮 Число турниров в которых вы участвовали: {count_of_tournaments}\n'
                '🎟🥇 Число турниров где вы выиграли: {count_of_win}\n'
            )
        ),
        Button(Const('🔙Назад'), id='tournaments_back', on_click=switch_to_main_menu),
        getter=get_profile,
        state=ProfileSG.start
    ),
)
