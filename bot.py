import asyncio
from aiogram import Bot, Dispatcher

from config import TELEGRAM_API_TOKEN
from handlers.user_handlers import setup_user_handlers
from db.session import init_db
from scripts.seed_workouts import seed_workouts
from ext_api.fatsecret_api import update_token


# Создаем экземпляры бота и диспетчера
if TELEGRAM_API_TOKEN is not None:

    bot = Bot(token=TELEGRAM_API_TOKEN)
    dp = Dispatcher()

    # Настраиваем middleware и обработчики
    setup_user_handlers(dp)
else:
    raise ImportError("Telegram API TOKEN is not specified")


async def token_refresher():
    while True:
        await update_token()
        await asyncio.sleep(60*60*23)


async def main():

    await init_db()
    await seed_workouts()

    refresher_task = asyncio.create_task(token_refresher())
    try:
        await dp.start_polling(bot)
    finally:
        refresher_task.cancel()
        await bot.session.close()

    print("Бот запущен!")

if __name__ == "__main__":
    asyncio.run(main())
