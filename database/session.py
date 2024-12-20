from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from environs import Env

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

env = Env()
env.read_env()

DB_URL = env('DB_URL')

engine = create_async_engine(DB_URL, echo=True)

session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class DataBaseSession(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool


    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data['session'] = session
            return await handler(event, data)