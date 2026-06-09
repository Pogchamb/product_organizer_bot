from aiogram.filters import Filter
from aiogram.types import Message


class GroupChat(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.chat.type in ("group", "supergroup")
