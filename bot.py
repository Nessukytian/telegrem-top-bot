from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from storage import add_channel, get_channels, remove_channel, map_message, get_chat_link
from collect_posts import get_most_liked_post
from config import OWNER_ID

router = Router()

@router.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer(
        "Привет! Я могу по команде /memes присылать самый залайканный пост за последние 24 часа "
        "из добавленных каналов.\n\n"
        "Добавить канал:\n"
        "/add_channel <имя_канала> <ссылка_на_чат>\n"
        "Удалить канал:\n"
        "/remove_channel <имя_канала>\n"
        "Список каналов — /list\n"
        "Получить мемы — /memes"
    )

@router.message(Command("add_channel"))
async def add_cmd(message: Message):
    if message.from_user.id != OWNER_ID:
        return
    parts = message.text.split()
    if len(parts) != 3:
        return await message.answer("Использование: /add_channel <имя_канала> <ссылка_на_чат>")
    channel_username = parts[1].lstrip("@")
    chat_link = parts[2]
    await add_channel(message.from_user.id, channel_username, chat_link)
    await message.answer(f"Канал @{channel_username} добавлен с чатом {chat_link}")

@router.message(Command("remove_channel"))
async def remove_cmd(message: Message):
    if message.from_user.id != OWNER_ID:
        return
    parts = message.text.split()
    if len(parts) != 2:
        return await message.answer("Использование: /remove_channel <имя_канала>")
    channel_username = parts[1].lstrip("@")
    await remove_channel(message.from_user.id, channel_username)
    await message.answer(f"Канал @{channel_username} удалён")

@router.message(Command("list"))
async def list_cmd(message: Message):
    if message.from_user.id != OWNER_ID:
        return
    chs = await get_channels(message.from_user.id)
    if not chs:
        await message.answer("Список пуст")
    else:
        text = "\n".join([f"@{c} → {l}" for c, l in chs])
        await message.answer(text)

@router.message(Command("memes"))
async def memes_cmd(message: Message):
    if message.from_user.id != OWNER_ID:
        return
    chs = await get_channels(message.from_user.id)
    if not chs:
        return await message.answer("Ни одного канала не добавлено.")
    await message.answer("Ищу самые залайканные посты за последние 24 часа…")
    for channel_username, chat_link in chs:
        post = await get_most_liked_post(channel_username)
        if not post:
            await message.answer(f"@{channel_username}: за 24 ч. постов не найдено.")
            continue
        sent = await message.bot.forward_message(message.from_user.id, post.chat.id, post.message_id)
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Перейти в чат", callback_data=f"open_chat:{sent.message_id}")]
            ]
        )
        await message.bot.send_message(message.from_user.id, " ", reply_markup=kb)
        await map_message(message.from_user.id, sent.message_id, chat_link)

@router.callback_query(F.data.startswith("open_chat:"))
async def open_chat_cb(callback: CallbackQuery):
    user_id = callback.from_user.id
    msg_id = int(callback.data.split(":", 1)[1])
    chat_link = await get_chat_link(user_id, msg_id)
    if chat_link:
        await callback.message.answer(f"Вот ссылка на чат: {chat_link}")
    await callback.answer()
