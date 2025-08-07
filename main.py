import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from bot import router
from storage import init_db

print("🚀 Бот запускается...")

async def main():
    await init_db()
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
