import logging
from datetime import datetime

from aiogram import F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, BotCommandScopeDefault, Message, PreCheckoutQuery, CallbackQuery, FSInputFile
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram.utils.payload import decode_payload
from aiogram_dialog import setup_dialogs, DialogManager, StartMode
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ad.ad import ad_dialog
from admin.admin import admin_main_dialog, admin_statistics_dialog, admin_create_tournaments_dialog, \
    admin_ref_link_dialog, admin_create_mandatory_task_dialog, admin_broadcast_create_dialog, \
    admin_active_tournaments_dialog, giveaway_dialog, add_admin_dialog, add_tickets_dialog
from create_bot import bot, dp, BASE_URL, WEBHOOK_PATH, HOST, PORT, ADMIN_ID
from database.models import TicketPurchase, User
from database.session import DataBaseSession, session_maker
from rules.rules import subscribe_dialog
from shop.shop import shop_dialog
from start.giveaway import user_giveaway_dialog
from start.profile import profile_dialog
from start.start import start_router, start_dialog, menu_dialog
from start.states import StartSG, RegistrationSG, MenuSG, UserGiveawaySG
from tournament.states import TournamentSG
from tournament.tournament import tournament_dialog


@dp.message(CommandStart(deep_link=True))
async def command_start_process(message: Message, dialog_manager: DialogManager, command: CommandObject):
    args = command.args
    inviter_id = None

    if args:
        decoded_payload = decode_payload(args)
        if decoded_payload.startswith("ref-"):
            inviter_id = int(decoded_payload.split("-")[1])

    await dialog_manager.start(
        state=RegistrationSG.start,
        mode=StartMode.RESET_STACK,
        data={"inviter_id": inviter_id}
    )


# @dp.message(Command("zxc"))
# async def cmd_zxc(message: Message, state: FSMContext):
#     await message.answer("Пожалуйста, отправьте видео.")
#
# @dp.message(F.video)
# async def process_video(message: Message, state: FSMContext):
#     file_id = message.video.file_id
#     print(f"Получено видео с file_id: {file_id}")
#     await message.answer(f"Спасибо за видео! Его file_id: {file_id}")


@dp.callback_query(lambda c: c.data.startswith("open_tournament:"))
async def process_tournament_callback(callback_query: CallbackQuery, dialog_manager: DialogManager):
    _, tournament_id, tournament_type = callback_query.data.split(":")
    await dialog_manager.start(
        state=TournamentSG.tournament_info,
        mode=StartMode.RESET_STACK,
        data={"selected_tournament_id": int(tournament_id), "tournament_type": tournament_type}
    )
    await callback_query.answer()


@dp.callback_query(lambda c: c.data.startswith("join_giveaway:"))
async def process_tournament_callback(callback_query: CallbackQuery, dialog_manager: DialogManager):
    _, giveaway_id = callback_query.data.split(":")
    await dialog_manager.start(
        state=UserGiveawaySG.giveaway_info,
        mode=StartMode.RESET_STACK,
        data={"selected_giveaway_id": int(giveaway_id)}
    )
    await callback_query.answer()


@dp.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=RegistrationSG.start, mode=StartMode.RESET_STACK)


async def set_commands():
    commands = [BotCommand(command='start', description='Главное меню'),
                BotCommand(command='chat_id', description='ID чата'), ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def on_startup() -> None:
    await set_commands()
    await bot.set_webhook(f"{BASE_URL}{WEBHOOK_PATH}")
    await bot.send_message(chat_id=ADMIN_ID, text='Бот запущен!')
    logger.info('Бот запущен!')


async def on_shutdown() -> None:
    await bot.send_message(chat_id=ADMIN_ID, text='Бот остановлен!')
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()


@dp.pre_checkout_query()
async def approve_order(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(True)


@dp.message(F.successful_payment)
async def process_successful_payment(message: Message, session: AsyncSession, dialog_manager: DialogManager):
    purchase_id = int(message.successful_payment.invoice_payload)

    purchase = await session.execute(select(TicketPurchase).where(TicketPurchase.id == purchase_id))
    purchase = purchase.scalar_one_or_none()

    if purchase:
        user = await session.execute(select(User).where(User.tg_id == purchase.user_id))
        user = user.scalar_one_or_none()

        if user:
            user.ticket_balance += purchase.amount
            purchase.updated = datetime.utcnow()

            await session.commit()

            await message.answer(
                f"🎉 Успешная покупка {purchase.amount} тикетов! Ваш текущий баланс: {user.ticket_balance} тикетов.",
            )
            # await dialog_manager.done()
            await dialog_manager.start(state=MenuSG.menu)


# @dp.message(Command("get_chat_id"))
# async def send_chat_id(message: Message):
#     if message.chat.type in ['group', 'supergroup', 'channel']:
#         chat_id = message.chat.id
#         await message.reply(f"ID текущего чата: {chat_id}")
#     else:
#         await message.reply("Эта команда работает только в каналах и группах.")


def main() -> None:
    dp.include_router(start_dialog)
    dp.include_router(menu_dialog)
    dp.include_router(subscribe_dialog)
    dp.include_router(ad_dialog)
    dp.include_router(admin_main_dialog)
    dp.include_router(admin_statistics_dialog)
    dp.include_router(admin_create_tournaments_dialog)
    dp.include_router(admin_ref_link_dialog)
    dp.include_router(shop_dialog)
    dp.include_router(tournament_dialog)
    dp.include_router(profile_dialog)
    dp.include_router(admin_create_mandatory_task_dialog)
    dp.include_router(admin_broadcast_create_dialog)
    dp.include_router(admin_active_tournaments_dialog)
    dp.include_router(giveaway_dialog)
    dp.include_router(user_giveaway_dialog)
    dp.include_router(add_admin_dialog)
    dp.include_router(add_tickets_dialog)
    setup_dialogs(dp)

    dp.startup.register(on_startup)

    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    dp.callback_query.middleware(CallbackAnswerMiddleware())

    app = web.Application()

    # обработчик запросов для работы с вебхуком
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )
    # Регистрируем обработчик запросов на определенном пути
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # Настраиваем приложение и связываем его с диспетчером и ботом
    setup_application(app, dp, bot=bot)

    # Запускаем веб-сервер на указанном хосте и порте
    web.run_app(app, host=HOST, port=PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    main()
