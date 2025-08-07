# gen_string_session.py

from pyrogram import Client
from config import API_ID, API_HASH

# При запуске скрипта вы введёте номер телефона и код, после чего
# в корне проекта появится файл "memes_collector.session".
# Скопируйте его содержимое в переменную STRING_SESSION в .env
if __name__ == "__main__":
    Client("memes_collector", api_id=API_ID, api_hash=API_HASH).run()
