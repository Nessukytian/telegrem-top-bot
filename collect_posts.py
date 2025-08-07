from datetime import datetime, timedelta, timezone
from pyrogram import Client
from config import API_ID, API_HASH

# Используем отдельный сессионный файл, чтобы не конфликтовать с ботом
SESSION_NAME = "memes_collector"

async def get_most_liked_post(channel_username: str):
    """
    Ищет в канале все сообщения за последние 24 часа
    и возвращает то, у которого больше всего реакций.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    best = None
    best_count = -1

    async with Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH) as app:
        async for msg in app.get_chat_history(channel_username, limit=200):
            if msg.date < cutoff:
                break
            # считаем лайки + сердечки, если есть реакции
            count = 0
            if msg.reactions:
                # Pyrogram 2.x: msg.reactions.recent_reactions хранит список объектов Reaction
                for r in msg.reactions.recent_reactions:
                    count += r.count
            # можно добавить другие эмодзи, если нужно

            if count > best_count:
                best = msg
                best_count = count

    return best
