from apscheduler.schedulers.asyncio import AsyncIOScheduler
from collect_posts import get_most_liked_post
from storage import get_channels, map_message
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_markup(msg_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("Открыть чат", callback_data=f"open_chat:{msg_id}")]
        ]
    )

async def daily_job(bot: Bot, user_id: int):
    channels = await get_channels(user_id)
    for channel_username, chat_link in channels:
        post = await get_most_liked_post(channel_username)
        if not post:
            continue
        sent = await bot.forward_message(user_id, post.chat.id, post.id)
        await bot.send_message(user_id, " ", reply_markup=get_markup(sent.message_id))
        await map_message(user_id, sent.message_id, chat_link)

def setup_scheduler(bot: Bot, user_id: int):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_job, 'cron', hour=19, args=[bot, user_id])
    scheduler.start()
