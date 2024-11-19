from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from environs import Env

env = Env()
env.read_env()

# переменные для работы
ADMIN_ID = env('ADMIN_ID')
BOT_TOKEN = env("BOT_TOKEN")
HOST = env("HOST")
PORT = int(env("PORT"))
WEBHOOK_PATH = f'/{BOT_TOKEN}'
BASE_URL = env("BASE_URL")

# инициализируем бота и диспетчера для работы с ним
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()