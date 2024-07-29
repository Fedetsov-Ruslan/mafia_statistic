from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command


user_private_router = Router()

@user_private_router.message(CommandStart())
async def start(message: Message):
    await message.answer('Статистика по мафии')


