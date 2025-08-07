# scheduler.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from collect_posts import get_most_liked_post
from storage import get_channels, map_message
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import pytz

# Московский часовой пояс
TZ = pytz.timezone("Europe/Moscow")

def get_markup(msg_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("Перейти в чат", callback_data=f"open_chat:{msg_id}")]
        ]
    )

async def daily_job(bot: Bot, user_id: int):
    channels = await get_channels(user_id)
    for channel_username, chat_link in channels:
        post = await get_most_liked_post(channel_username)
        if not post:
            continue
        # Пересылаем самый залайканный пост в личный чат
        sent = await bot.forward_message(user_id, post.chat.id, post.id)
        # Добавляем кнопку «Перейти в чат» под пересланным сообщением
        await bot.send_message(
            user_id,
            " ",
            reply_markup=get_markup(sent.message_id)
        )
        # Сохраняем соответствие message_id → chat_link
        await map_message(user_id, sent.message_id, chat_link)

def setup_scheduler(bot: Bot, user_id: int):
    scheduler = AsyncIOScheduler(timezone=TZ)
    scheduler.add_job(
        daily_job,
        trigger='cron',
        hour=19,
        minute=0,
        args=[bot, user_id],
        timezone=TZ
    )
    scheduler.start()
