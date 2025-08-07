from datetime import datetime, timedelta, timezone
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

SESSION_NAME = "memes_collector"

async def get_top_posts(channel_username: str):
    """
    Возвращает кортеж (best_any, best_original):
    - best_any      — сообщение с наибольшим числом реакций за 24 ч (включая пересылы).
    - best_original — лучшее сообщение, написанное в самом канале (не пересыл).
    Оба могут быть None, если не найдено.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    best_any = None
    best_any_count = -1
    best_orig = None
    best_orig_count = -1

    async with Client(
        SESSION_NAME,
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN
    ) as app:
        async for msg in app.get_chat_history(channel_username, limit=200):
            if msg.date < cutoff:
                break

            # Считаем "лайки" через реакции
            count = 0
            if msg.reactions:
                for r in msg.reactions.recent_reactions:
                    count += r.count

            # Общий топ
            if count > best_any_count:
                best_any = msg
                best_any_count = count

            # Топ среди оригинальных (не-forwarded)
            if not msg.forward_from_chat and count > best_orig_count:
                best_orig = msg
                best_orig_count = count

    return best_any, best_orig
