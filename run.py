import os
import asyncio


from aiogram.types import BotCommandScopeAllPrivateChats
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from app.handlers.user_private import user_private_router





async def main():
    load_dotenv()

    bot = Bot(token=os.getenv("TG_TOKEN"))
    dp = Dispatcher()
    dp.include_router(user_private_router)

    try:
    #   await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
      await dp.start_polling(bot)
    except KeyboardInterrupt:
        await bot.close()
        print("bot dont active")


if __name__ == "__main__":
    asyncio.run(main())