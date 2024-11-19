from aiogram.types import Message, CallbackQuery
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

from admin.states import AdminBroadcastSG


async def photo_check(message: Message,
        widget: MessageInput,
        dialog_manager: DialogManager) -> None:
    if not message.photo[-1].file_id:
        await message.answer(text='Отпрвьте фото (не файл). Желательный формат - jpg')

    dialog_manager.dialog_data['photo'] = message.photo[-1].file_id
    await dialog_manager.next()


async def photos_check(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    if not message.photo:
        await message.answer("Отправьте фото (не файл). Желательный формат - jpg")
        return

    # Получаем или создаем MediaGroupBuilder
    media_group = dialog_manager.dialog_data.get("media_group", MediaGroupBuilder())

    # Добавляем фото в MediaGroupBuilder
    media_group.add_photo(media=message.photo[-1].file_id)

    # Сохраняем обновленный MediaGroupBuilder
    dialog_manager.dialog_data["media_group"] = media_group

    # Получаем количество фото через build()
    photo_count = len(media_group.build())

    await message.answer(
        f"Фото добавлено. Всего фото: {photo_count}. Отправьте еще фото или перейдите к следующему шагу.")


async def skip_input_btn(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['button_text'] = ''
    dialog_manager.dialog_data['button_link'] = ''
    await dialog_manager.switch_to(AdminBroadcastSG.preview)

