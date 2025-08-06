import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, OWNER_ID
from bot import router
from scheduler import setup_scheduler
from storage import init_db

print("🚀 Бот запускается...")

async def main():
    await init_db()
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(router)

    setup_scheduler(bot, OWNER_ID)

    await dp.start_polling(bot)

if name == "__main__":
    asyncio.run(main())
