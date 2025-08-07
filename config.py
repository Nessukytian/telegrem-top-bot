import os
from dotenv import load_dotenv

load_dotenv()  # читает .env из корня

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID    = int(os.getenv("API_ID"))
API_HASH  = os.getenv("API_HASH")
OWNER_ID  = int(os.getenv("OWNER_ID"))
