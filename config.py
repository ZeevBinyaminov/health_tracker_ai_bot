import os
import logging

from dotenv import load_dotenv

# Суперподробное логирование для отладки
# logging.basicConfig(level=logging.DEBUG)

# aiohttp_logger = logging.getLogger("aiohttp")
# aiohttp_logger.setLevel(logging.DEBUG)

load_dotenv()

FATSECRET_CLIENT_ID = os.getenv('FATSECRET_CLIENT_ID')
FATSECRET_CLIENT_SECRET = os.getenv('FATSECRET_CLIENT_SECRET')

TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

if not FATSECRET_CLIENT_ID or not FATSECRET_CLIENT_SECRET or not TELEGRAM_API_TOKEN:
    raise ValueError("Missing required environment variables")
