# bot.py

from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from storage import add_channel, get_channels, remove_channel, map_message, get_chat_link
from collect_posts import get_top_posts
from config import OWNER_ID

router = Router()

@router.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer(
        "👋 Привет! Я могу по команде <code>/memes</code> присылать самый залайканный пост за последние 24 ч из добавленных каналов.\n\n"
        "• Добавить канал:\n"
        "  <code>/add_channel имя_канала ссылка_на_чат</code>\n"
        "• Удалить канал:\n"
        "  <code>/remove_channel имя_канала</code>\n"
        "• Список каналов — <code>/list</code>\n"
        "• Получить мемы — <code>/memes</code>",
        parse_mode="HTML"
    )

@router.message(Command("add_channel"))
async def add_cmd(message: Message):
    if message.from_user.id != OWNER_ID:
        return
    parts = message.text.split()
    if len(parts) != 3:
        return await message.answer(
            "❗️ Использование:\n<code>/add_channel имя_канала ссылка_на_чат</code>",
            parse_mode="HTML"
        )
    channel_username = parts[1].lstrip("@")
    chat_link = parts[2]
    await add_channel(message.from_user.id, channel_username, chat_link)
    await message.answer(
        f"✅ Канал @{channel_username} добавлен с чатом <code>{chat_link}</code>",
        parse_mode="HTML"
    )

@router.message(Command("remove_channel"))
async def remove_cmd(message: Message):
    if message.from_user.id != OWNER_ID:
        return
    parts = message.text.split()
    if len(parts) != 2:
        return await message.answer(
            "❗️ Использование:\n<code>/remove_channel имя_канала</code>",
            parse_mode="HTML"
        )
    channel_username = parts[1].lstrip("@")
    await remove_channel(message.from_user.id, channel_username)
    await message.answer(
        f"🗑 Канал @{channel_username} удалён",
        parse_mode="HTML"
    )

@router.message(Command("list"))
async def list_cmd(message: Message):
    if message.from_user.id != OWNER_ID:
        return
    chs = await get_channels(message.from_user.id)
    if not chs:
        await message.answer("Список каналов пуст 📝")
    else:
        text = "\n".join([f"@{c} → <code>{l}</code>" for c, l in chs])
        await message.answer(text, parse_mode="HTML")

@router.message(Command("memes"))
async def memes_cmd(message: Message):
    if message.from_user.id != OWNER_ID:
        return

    channels = await get_channels(message.from_user.id)
    if not channels:
        return await message.answer("❗️ Ни одного канала не добавлено.")

    await message.answer("🔍 Ищу топ-мемы за последние 24 ч…")

    for channel_username, chat_link in channels:
        best_any, best_orig = await get_top_posts(channel_username)

        if not best_any:
            await message.answer(f"@{channel_username}: за 24 ч постов не найдено.")
            continue

        # 1) Пересылаем лучший (любой)
        sent_any = await message.bot.forward_message(
            message.from_user.id,
            best_any.chat.id,
            best_any.message_id
        )
        kb_any = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Перейти в чат", callback_data=f"open_chat:{sent_any.message_id}")
        )
        await message.bot.send_message(message.from_user.id, " ", reply_markup=kb_any)
        await map_message(message.from_user.id, sent_any.message_id, chat_link)

        # 2) Если это был пересыл и есть оригинал — пересылаем его
        if best_any.forward_from_chat and best_orig:
            sent_orig = await message.bot.forward_message(
                message.from_user.id,
                best_orig.chat.id,
                best_orig.message_id
            )
            kb_orig = InlineKeyboardMarkup().add(
                InlineKeyboardButton("Перейти в чат", callback_data=f"open_chat:{sent_orig.message_id}")
            )
            await message.bot.send_message(message.from_user.id, " ", reply_markup=kb_orig)
            await map_message(message.from_user.id, sent_orig.message_id, chat_link)

@router.callback_query(F.data.startswith("open_chat:"))
async def open_chat_cb(callback: CallbackQuery):
    user_id = callback.from_user.id
    msg_id = int(callback.data.split(":", 1)[1])
    chat_link = await get_chat_link(user_id, msg_id)
    if chat_link:
        await callback.message.answer(
            f"🔗 Вот ссылка на чат: <code>{chat_link}</code>",
            parse_mode="HTML"
        )
    await callback.answer()
