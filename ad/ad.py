from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.media import StaticMedia, DynamicMedia
from aiogram_dialog.widgets.text import Const

from ad.states import AdSG
from utils.switcher import switch_to_main_menu


async def get_video(dialog_manager: DialogManager, **kwargs):
    return {
        'video': MediaAttachment(ContentType.VIDEO, file_id=MediaId('BAACAgIAAxkBAAIWIGc7j0nqEoiBf69gCu4O046OdZikAAKCWgAC_wbhSdI3gALYS2bsNgQ'))
    }

ad_dialog = Dialog(
    Window(
        DynamicMedia('video'),
        Const('<a href="https://t.me/koshmrUCbot" style="color: blue;">Халява от КОШМАРА</a> — <i>'
              'первый бот в котором ты сможешь зарабатывать UC и выводить их в телеграмм '
              'боте</i>\n\n'
              'Выполняй простые задания🩶— Получай UC\n'
              'Приглашай друзей🤍 — <b>Получай UC и 10% с их заработка</b>\n\n'
              '<i>С бота уже выведено более 300.000 UC,так что скорее переходи</i>⬇️'),

        # Кнопки
        Button(Const('🔙 Назад'), id='to_main_menu', on_click=switch_to_main_menu),

        # Остальное
        getter=get_video,
        state=AdSG.start,
    )
)

