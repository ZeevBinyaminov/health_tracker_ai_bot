import os
import logging

from dotenv import load_dotenv

# Суперподробное логирование для отладки
logging.basicConfig(level=logging.DEBUG)

aiohttp_logger = logging.getLogger("aiohttp")
aiohttp_logger.setLevel(logging.DEBUG)

load_dotenv()

FATSECRET_CLIENT_ID = os.getenv('FATSECRET_CLIENT_ID')
FATSECRET_CLIENT_SECRET = os.getenv('FATSECRET_CLIENT_SECRET')

TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")


POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

DATABASE_URL = (
    "postgresql+asyncpg://"
    f"{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

if not FATSECRET_CLIENT_ID or not FATSECRET_CLIENT_SECRET or not TELEGRAM_API_TOKEN:
    raise ValueError("Missing required environment variables")
