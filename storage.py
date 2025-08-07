import aiosqlite

DB_FILE = "bot.db"

async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            channel_username TEXT,
            chat_link TEXT
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS message_map (
            user_id INTEGER,
            message_id INTEGER,
            chat_link TEXT
        )""")
        await db.commit()

async def add_channel(user_id: int, channel_username: str, chat_link: str):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT INTO channels (user_id, channel_username, chat_link) VALUES (?, ?, ?)",
            (user_id, channel_username, chat_link)
        )
        await db.commit()

async def get_channels(user_id: int):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute(
            "SELECT channel_username, chat_link FROM channels WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            return await cursor.fetchall()  # List of (username, link)

async def remove_channel(user_id: int, channel_username: str):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "DELETE FROM channels WHERE user_id = ? AND channel_username = ?",
            (user_id, channel_username)
        )
        await db.commit()

async def map_message(user_id: int, message_id: int, chat_link: str):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT INTO message_map (user_id, message_id, chat_link) VALUES (?, ?, ?)",
            (user_id, message_id, chat_link)
        )
        await db.commit()

async def get_chat_link(user_id: int, message_id: int):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute(
            "SELECT chat_link FROM message_map WHERE user_id=? AND message_id=?",
            (user_id, message_id)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None
