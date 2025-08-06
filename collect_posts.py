from pyrogram import Client
import datetime
from config import API_ID, API_HASH

async def get_most_liked_post(channel_username: str):
    async with Client("my_session", api_id=API_ID, api_hash=API_HASH) as app:
        end = datetime.datetime.now()
        start = end - datetime.timedelta(days=1)

        messages = []
        async for msg in app.get_chat_history(channel_username, limit=100):
            if msg.date < start:
                break
            if msg.reactions:
                total = sum(r.count for r in msg.reactions)
                messages.append((msg, total))

        if not messages:
            return None
        return max(messages, key=lambda x: x[1])[0]
