# bot.py

import asyncio
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
        "👋 Привет! Я по команде <code>/memes</code> пришлю топ-мемы за последние 24 ч из ваших каналов.\n\n"
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
            "❗️ Использование: <code>/add_channel имя_канала ссылка_на_чат</code>",
            parse_mode="HTML"
        )
    chan, chat_link = parts[1].lstrip("@"), parts[2]
    await add_channel(message.from_user.id, chan, chat_link)
    await message.answer(
        f"✅ Канал @{chan} добавлен → {chat_link}",
        parse_mode="HTML"
    )

@router.message(Command("remove_channel"))
async def remove_cmd(message: Message):
    if message.from_user.id != OWNER_ID:
        return
    parts = message.text.split()
    if len(parts) != 2:
        return await message.answer(
            "❗️ Использование: <code>/remove_channel имя_канала</code>",
            parse_mode="HTML"
        )
    chan = parts[1].lstrip("@")
    await remove_channel(message.from_user.id, chan)
    await message.answer(f"🗑 Канал @{chan} удалён", parse_mode="HTML")

@router.message(Command("list"))
async def list_cmd(message: Message):
    if message.from_user.id != OWNER_ID:
        return
    lst = await get_channels(message.from_user.id)
    if not lst:
        return await message.answer("Список каналов пуст 📝")
    text = "\n".join(f"@{c} → {l}" for c, l in lst)
    await message.answer(text, parse_mode="HTML")

@router.message(Command("memes"))
async def memes_cmd(message: Message):
    if message.from_user.id != OWNER_ID:
        return

    channels = await get_channels(message.from_user.id)
    if not channels:
        return await message.answer("❗️ Нет добавленных каналов.")

    await message.answer("🔍 Собираю топ-мемы за последние 24 ч…")

    for chan, chat_link in channels:
        best_any, best_orig = await asyncio.to_thread(get_top_posts, chan)
        if not best_any:
            await message.answer(f"@{chan}: нет постов за 24 ч.")
            continue

        # 1) переслать best_any
        sent = await message.bot.forward_message(
            chat_id=message.from_user.id,
            from_chat_id=f"@{chan}",
            message_id=best_any.message_id
        )
        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Перейти в чат", callback_data=f"open_chat:{sent.message_id}")
        )
        await message.bot.send_message(message.from_user.id, " ", reply_markup=kb)
        await map_message(message.from_user.id, sent.message_id, chat_link)

        # 2) если это был forwarded и есть best_orig — переслать его
        if best_any.forward_from_chat and best_orig:
            sent2 = await message.bot.forward_message(
                chat_id=message.from_user.id,
                from_chat_id=f"@{chan}",
                message_id=best_orig.message_id
            )
            kb2 = InlineKeyboardMarkup().add(
                InlineKeyboardButton("Перейти в чат", callback_data=f"open_chat:{sent2.message_id}")
            )
            await message.bot.send_message(message.from_user.id, " ", reply_markup=kb2)
            await map_message(message.from_user.id, sent2.message_id, chat_link)

@router.callback_query(F.data.startswith("open_chat:"))
async def open_chat_cb(callback: CallbackQuery):
    user_id = callback.from_user.id
    msg_id = int(callback.data.split(":", 1)[1])
    link = await get_chat_link(user_id, msg_id)
    if link:
        await callback.message.answer(f"🔗 Ссылка на чат: {link}")
    await callback.answer()
