# Телеграм-бот для трекинга здоровья

Бот для учета воды, калорий и тренировок.  
Использует FatSecret для поиска продуктов, OpenWeatherMap для корректировки нормы воды и PostgreSQL для хранения данных.

## Возможности
- Заполнение профиля и расчет суточных норм
- Логирование воды, еды и тренировок
- Дневная сводка прогресса
- Графики за последние 7 дней по воде и калориям

## Команды
- `/start` или `/help` - список команд
- `/set_profile` - заполнить/обновить профиль
- `/log_water` - записать воду
- `/log_food` - записать еду
- `/log_workout` - записать тренировку
- `/check_progress` - статистика за сегодня
- `/get_cal_stats` - график калорий за 7 дней
- `/get_water_stats` - график воды за 7 дней

## Требования
- Python 3.11+
- PostgreSQL
- FatSecret API credentials
- OpenWeatherMap API key
- Telegram bot token

## Переменные окружения
Создайте файл `.env`:
```
TELEGRAM_API_TOKEN=...
OPENWEATHERMAP_API_KEY=...
FATSECRET_CLIENT_ID=...
FATSECRET_CLIENT_SECRET=...

POSTGRES_USER=zeevbin
POSTGRES_PASSWORD=...
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=health_tracker
```

`DATABASE_URL` собирается внутри приложения из этих параметров.


## Запуск через Docker
```
docker compose up --build
```

При запуске в Docker установите `POSTGRES_HOST=db` в `.env`.

## Примечания
- Поиск еды работает надежнее по английским названиям.
- Графики строятся через matplotlib и отправляются как PNG.
