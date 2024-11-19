import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from environs import Env
from redis.asyncio import Redis

env = Env()
env.read_env()

BOT_TOKEN = env('BOT_TOKEN')
REDIS_HOST = env('REDIS_HOST', 'localhost')
REDIS_PORT = env.int('REDIS_PORT', 6379)
REDIS_PASSWORD = env('REDIS_PASSWORD', None)

WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 8000
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = "my-secret"
BASE_WEBHOOK_URL = "https://aiogram.dev"

router = Router()


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)


async def main():
    redis = Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        encoding="utf-8",
        decode_responses=True
    )

    storage = RedisStorage(redis, state_ttl=3600, data_ttl=3600)

    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    dp.startup.register(on_startup)

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEB_SERVER_HOST, WEB_SERVER_PORT)
    await site.start()

    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()
        await bot.session.close()
        await redis.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
