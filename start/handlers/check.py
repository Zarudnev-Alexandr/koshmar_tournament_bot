from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import models


async def pubg_id_check(text: Any) -> str:
    text = str(text)
    if not (text.isdigit() and text.startswith("51") and 8 <= len(text) <= 12):
        raise ValueError("Некорректный PUBG ID: должен начинаться с '51' и иметь от 8 до 12 цифр.")
    return text

