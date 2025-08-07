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
        "👋 Я могу по команде <code>/memes</code> присылать топ-мемы за последние 24 ч из добавленных каналов.\n\n"
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
    chan, link = parts[1].lstrip("@"), parts[2]
    await add_channel(message.from_user.id, chan, link)
    await message.answer(
        f"✅ Канал @{chan} добавлен → {link}",
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
    chan = parts[1].lstrip("@")
    await remove_channel(message.from_user.id, chan)
    await message.answer(f"🗑 Канал @{chan} удалён", parse_mode="HTML")

@router.message(Command("list"))
async def list_cmd(message: Message):
    if message.from_user.id != OWNER_ID:
        return
    chs = await get_channels(message.from_user.id)
    if not chs:
        return await message.answer("Список каналов пуст 📝")
    text = "\n".join(f"@{c} → {l}" for c, l in chs)
    await message.answer(text, parse_mode="HTML")

@router.message(Command("memes"))
async def memes_cmd(message: Message):
    if message.from_user.id != OWNER_ID:
        return

    chans = await get_channels(message.from_user.id)
    if not chans:
        return await message.answer("❗️ Ни одного канала не добавлено.")

    await message.answer("🔍 Ищу топ-мемы за последние 24 ч…")
    for chan, chat_link in chans:
        best_any, best_orig = await asyncio.to_thread(get_top_posts, chan)
        if not best_any:
            await message.answer(f"@{chan}: за 24 ч постов не найдено.")
            continue

        # Извлечь message_id из data-post
        data_post = best_any["data-post"]  # e.g. "channel/12345"
        msg_id = int(data_post.split("/", 1)[1])

        sent = await message.bot.forward_message(
            message.from_user.id,
            f"@{chan}",
            msg_id
        )
        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Перейти в чат", callback_data=f"open_chat:{sent.message_id}")
        )
        await message.bot.send_message(message.from_user.id, " ", reply_markup=kb)
        await map_message(message.from_user.id, sent.message_id, chat_link)

        # Если это был пересыл и есть оригинал — тоже отправить
        if best_any.find("a", class_="tgme_widget_message_forwarded") and best_orig:
            dp2 = best_orig["data-post"]
            msg2 = int(dp2.split("/", 1)[1])
            sent2 = await message.bot.forward_message(
                message.from_user.id,
                f"@{chan}",
                msg2
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
        await callback.message.answer(
            f"🔗 Ссылка на чат: {link}",
            parse_mode="HTML"
        )
    await callback.answer()
