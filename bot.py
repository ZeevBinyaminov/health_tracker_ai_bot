import asyncio
from aiogram import Bot, Dispatcher
from config import TELEGRAM_API_TOKEN
from handlers.user_handlers import setup_user_handlers
from db.session import init_db

# Создаем экземпляры бота и диспетчера
bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher()

# Настраиваем middleware и обработчики
setup_user_handlers(dp)

# async def on_startup():


async def main():
    print("Бот запущен!")
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
