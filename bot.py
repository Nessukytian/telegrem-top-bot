from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from storage import add_channel, get_channels, remove_channel, get_chat_link
from config import OWNER_ID

router = Router()

@router.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer("Привет! Я пересылаю самый залайканный пост из каждого канала. Используй /add_channel.")

@router.message(Command("add_channel"))
async def add_cmd(message: Message):
    if message.from_user.id != OWNER_ID:
        return
    parts = message.text.strip().split()
    if len(parts) != 3:
        await message.answer("Формат: /add_channel @канал ссылка_на_чат")
        return
    _, channel, link = parts
    await add_channel(message.from_user.id, channel, link)
    await message.answer(f"Канал {channel} добавлен")

@router.message(Command("remove_channel"))
async def rem_cmd(message: Message):
    if message.from_user.id != OWNER_ID:
        return
    parts = message.text.strip().split()
    if len(parts) != 2:
        await message.answer("Формат: /remove_channel @канал")
        return
    _, channel = parts
    await remove_channel(message.from_user.id, channel)
    await message.answer(f"Канал {channel} удалён")

@router.message(Command("list"))
async def list_cmd(message: Message):
    if message.from_user.id != OWNER_ID:
        return
    chs = await get_channels(message.from_user.id)
    text = "\n".join([f"{c} → {l}" for c, l in chs]) or "Список пуст"
    await message.answer(text)

@router.callback_query(F.data.startswith("open_chat:"))
async def open_chat_cb(callback: CallbackQuery):
    msg_id = int(callback.data.split(":")[1])
    chat_link = await get_chat_link(callback.from_user.id, msg_id)
    if chat_link:
        await callback.message.answer(f"Вот ссылка на чат: {chat_link}")
    await callback.answer()
