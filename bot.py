from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from storage import add_channel, get_channels, remove_channel, get_chat_link
from config import OWNER_ID

router = Router()

@router.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer(
        "Привет! Я каждый день в 19:00 пришлю самый залайканный пост из добавленных каналов.\n"
        "Чтобы добавить канал, используй:\n"
        "/add_channel <имя_канала> <ссылка_на_чат>\n"
        "Чтобы удалить —\n"
        "/remove_channel <имя_канала>\n"
        "Список каналов — /list"
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

@router.callback_query(F.data.startswith("open_chat:"))
async def open_chat_cb(callback: CallbackQuery):
    user_id = callback.from_user.id
    msg_id = int(callback.data.split(":", 1)[1])
    chat_link = await get_chat_link(user_id, msg_id)
    if chat_link:
        await callback.message.answer(f"Вот ссылка на чат: {chat_link}")
    await callback.answer()
