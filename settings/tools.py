from functools import wraps
from create_bot import admins
from aiogram.types import Message

def is_admin(user_id: int) -> bool:
    return user_id in admins

def admin_only(handler):
    @wraps(handler)
    async def wrapper(message: Message, *args, **kwargs):
        if not is_admin(message.from_user.id):
            await message.reply("⛔ У тебя нет доступа к админ-командам")
            return None
        return await handler(message, *args, **kwargs)
    return wrapper