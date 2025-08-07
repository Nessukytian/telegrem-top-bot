from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from storage import add_channel, get_channels, remove_channel, map_message, get_chat_link
from collect_posts import get_top_posts
from config import OWNER_ID

router = Router()

# ... остальные хендлеры (/start, /add_channel и т.д.) без изменений ...

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

        # 1) Пересылаем лучший (any)
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

        # 2) Если это был пересыл, и есть оригинал — пересылаем его тоже
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
    # ... без изменений ...
