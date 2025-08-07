# collect_posts.py

from datetime import datetime, timedelta, timezone
from pyrogram import Client
from config import API_ID, API_HASH, STRING_SESSION

SESSION_NAME = "memes_collector"

async def get_top_posts(channel_username: str):
    """
    Возвращает два объекта Message:
      best_any  — топ по реакциям (включая пересылы)
      best_orig — топ оригинальных сообщений
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    best_any = best_orig = None
    cnt_any = cnt_orig = -1

    async with Client(
        SESSION_NAME,
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=STRING_SESSION
    ) as app:
        async for msg in app.get_chat_history(channel_username, limit=200):
            if msg.date < cutoff:
                break
            # сумма всех реакций
            total = sum(r.count for r in (msg.reactions.recent_reactions or []))
            if total > cnt_any:
                best_any, cnt_any = msg, total
            if not msg.forward_from_chat and total > cnt_orig:
                best_orig, cnt_orig = msg, total

    return best_any, best_orig
