from aiogram import Router, Dispatcher, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from states import ProfileForm, FoodForm, WorkoutForm, WaterForm
from keyboards.user_keyboards import (
    sex_choice_keyboard,
    generate_food_inline_keyboard,
    generate_workout_inline_keyboard,
)

from schemas.user import UserSchema, NormsSchema, StatisticsSchema
from db.users import upsert_user_profile, add_statistics, get_progress_from_statistics, get_user_norms
from db.services import get_workouts
from db.analysis import build_water_plot, build_kcal_plot
from db.stats import get_last_7_days_stats
from ext_api.weathermap_api import get_weather_data
from ext_api.fatsecret_api import get_top_n_positions
from filters.user_filters import RegisteredUserFilter

router = Router()
router.message.filter(RegisteredUserFilter())
router.callback_query.filter(RegisteredUserFilter())


@router.callback_query(F.data == "cancel")
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await callback.message.answer("Нечего отменять")
        await callback.answer()
        return
    await state.clear()
    await callback.message.edit_text(text="Запрос отменен.", reply_markup=None)
    await callback.answer()


@router.message(Command("start", "help"))
async def start_handler(message: Message):
    await message.answer(
        "Доступные команды:\n"
        "/start или /help - список доступных команд\n"
        "/set_profile - заполнить профиль\n"
        "/log_water - записать потребление воды\n"
        "/log_food - записать потребление пищи\n"
        "/log_workout - записать тренировку\n"
        "/check_progress - посмотреть статистику за сегодня\n"
        "/get_cal_stats - посмотреть статистику по калориям за последние 7 дней\n"
        "/get_water_stats - посмотреть статистику по воде за последние 7 дней\n"
    )


@router.message(Command("set_profile"))
async def start_profile_form(message: Message, state: FSMContext):
    await message.answer("Давайте заполним Ваш профиль!\n"
                         "Как Вас зовут?")
    await state.set_state(ProfileForm.name)


@router.message(ProfileForm.name)
async def process_name(message: Message, state: FSMContext):
    name = message.text
    if name is None or not name.isalpha():
        await message.answer("Пожалуйста, введите корректное имя (только буквы).")
        return
    await state.update_data(name=name)
    await message.answer("Какой у Вас вес (в кг)?")
    await state.set_state(ProfileForm.weight)


@router.message(ProfileForm.weight)
async def process_weight(message: Message, state: FSMContext):
    weight = message.text
    if weight is None or not weight.isdigit() or not int(weight) > 0:
        await message.answer("Пожалуйста, введите вес в корректном формате (число).")
        return
    await state.update_data(weight=int(weight))
    await message.answer("Сколько Вам лет?")
    await state.set_state(ProfileForm.age)


@router.message(ProfileForm.age)
async def process_age(message: Message, state: FSMContext):
    age = message.text
    if age is None or not age.isdigit() or not (0 < int(age) < 120):
        await message.answer("Пожалуйста, введите возраст в корректном формате (число от 1 до 119).")
        return
    await state.update_data(age=int(age))
    await message.answer("Ваш пол?", reply_markup=sex_choice_keyboard)
    await state.set_state(ProfileForm.sex)


@router.callback_query(ProfileForm.sex)
async def process_sex(callback_query: CallbackQuery, state: FSMContext):
    sex = callback_query.data
    await state.update_data(sex=sex)

    await callback_query.message.edit_reply_markup(None)
    await callback_query.message.answer("Ваш рост (в см)?")

    await state.set_state(ProfileForm.height)
    await callback_query.answer()


@router.message(ProfileForm.height)
async def process_height(message: Message, state: FSMContext):
    height = message.text
    if height is None or not height.isdigit() or not (50 < int(height) < 300):
        await message.answer("Пожалуйста, введите рост в корректном формате (число от 51 до 299).")
        return
    await state.update_data(height=int(height))
    await message.answer("В каком городе Вы живёте?")
    await state.set_state(ProfileForm.city)


@router.message(ProfileForm.city)
async def process_city(message: Message, state: FSMContext):
    city = message.text
    if city is None or not city.isalpha():
        await message.answer("Пожалуйста, введите корректное название города (только буквы).")
        return
    await state.update_data(city=city)
    await message.answer("Какой у Вас уровень дневной активности? (в минутах)")
    await state.set_state(ProfileForm.day_activity)


def calc_kcal_norm(sex, age, weight, height, day_activity):
    """
    Harris-Benedict equation for callories norm calculation
    https://primekraft.ru/articles/kak-rasschitat-sutochnuyu-kalorijnost-ratsiona-formulyi-rascheta/?srsltid=AfmBOopgfAGvZSQhMNzeetVotlfhcCgj_uOGtxe2hHHkiQz7g62d1wuI
    """
    activity_coef = 1.2
    if day_activity < 30:
        activity_coef = 1.375
    if 30 <= day_activity < 60:
        activity_coef = 1.55
    elif 60 <= day_activity < 120:
        activity_coef = 1.7
    else:
        activity_coef = 1.9

    kcal_norm = -1
    if sex == 'woman':
        kcal_norm = 655.1 + 9.563*weight + 1.85*height - 4.676*age
    elif sex == 'man':
        kcal_norm = 66.5 + 13.75*weight + 5.003*height - 6.775*age

    return kcal_norm * activity_coef


@router.message(ProfileForm.day_activity)
async def process_day_activity(message: Message, state: FSMContext):
    day_activity = message.text
    if day_activity is None or not day_activity.isnumeric():
        await message.answer("Пожалуйста, введите корректное значение дневной активности (кол-во минут).")
        return
    await state.update_data(day_activity=int(day_activity))
    await message.answer("Какова ваша норма калорий в день?")
    await state.set_state(ProfileForm.kcal_norm)


async def calc_water_norm(weight, day_activity, city):
    base_norm = weight * 30
    additional_for_activity = 500 * \
        int(60/day_activity) if day_activity > 0 else 0
    current_weather = await get_weather_data(city)
    additional_for_weather = 500 if current_weather.get(
        'temperature', 0) > 25 else 0
    return base_norm + additional_for_activity + additional_for_weather


@router.message(ProfileForm.kcal_norm)
async def process_kcal_norm(message: Message, state: FSMContext):
    kcal_norm = message.text
    user_data = await state.get_data()

    if kcal_norm is None or not kcal_norm.isdigit():
        await message.answer("Пожалуйста, введите корректное значение нормы калорий (положительное число).")
        return
    elif int(kcal_norm) == 0:
        kcal_norm = calc_kcal_norm(user_data['sex'], user_data['age'],
                                   user_data['weight'], user_data['height'],
                                   user_data['day_activity'])

    water_norm = await calc_water_norm(user_data['weight'], user_data['day_activity'], user_data['city'])

    await state.update_data(kcal_norm=int(kcal_norm))
    await state.update_data(water_norm=int(water_norm))
    await state.update_data(telegram_id=message.from_user.id)

    user_data = await state.get_data()

    user_schema = UserSchema(**user_data)
    norms_schema = NormsSchema(**user_data)

    await upsert_user_profile(
        user_schema.model_dump(),
        norms_schema.model_dump()
    )

    await message.answer("Профиль заполнен!\n"
                         "Введите /help, чтобы посмотреть список команд.")

    await state.clear()


@router.message(Command('log_water'))
async def start_water_form(message: Message, state: FSMContext):
    await message.answer("Введите количество выпитой воды (в мл)")
    await state.set_state(WaterForm.amount)


@router.message(WaterForm.amount)
async def process_water_amount(message: Message, state: FSMContext):
    water_amount = message.text
    if water_amount is None or not water_amount.isnumeric():
        await message.answer("Неправильный формат объема выпитой воды, введите число (кол-во мл)")
        return
    water_amount = int(water_amount)

    # выводить текущее потребление воды
    statistics_schema = StatisticsSchema(
        telegram_id=message.from_user.id, amount=water_amount, action='water')
    await add_statistics(statistics_schema.model_dump())

    await message.answer(f"Действие записано.")
    await state.clear()


@router.message(Command('log_food'))
async def start_food_form(message: Message, state: FSMContext):
    await message.answer("Введите название продукта (на английском).")
    await state.set_state(FoodForm.food_name)


@router.message(FoodForm.food_name)
async def process_food_name(message: Message, state: FSMContext):
    food_query = message.text
    if food_query is None:
        await message.answer("Неверное формат сообщения, ведите название продукта (на английском).")
        return

    food_list = await get_top_n_positions(food_query)

    if not food_list:
        await message.answer("Данного продукта нет в нашей базе, попробуйте ввести другой запрос.")
        return

    food_inline_keyboard = generate_food_inline_keyboard(food_list)

    await message.answer("Выберите продукт", reply_markup=food_inline_keyboard)
    await state.set_state(FoodForm.food_choice)


@router.callback_query(FoodForm.food_choice)
async def process_food_choice(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(kcal_per_100g=float(callback_query.data))

    await callback_query.message.edit_reply_markup(None)
    await callback_query.message.answer("Сколько грамм Вы съели ?")

    await state.set_state(FoodForm.amount)
    await callback_query.answer()


@router.message(FoodForm.amount)
async def process_food_amount(message: Message, state: FSMContext):
    food_amount = message.text

    if food_amount is None or not food_amount.isdigit():
        await message.answer("Пожалуйста, введите корректное в граммах (положительное число).")
        return

    data = await state.get_data()
    food_amount = int(food_amount)
    total_kcal = int(data['kcal_per_100g'] / 100 * food_amount)

    # выводить текущее потребление еды
    statistics_schema = StatisticsSchema(
        telegram_id=message.from_user.id, amount=total_kcal, action='food')
    await add_statistics(statistics_schema.model_dump())

    await message.answer(f"Действие записано.")
    await state.clear()


@router.message(Command('log_workout'))
async def start_workout_form(message: Message, state: FSMContext):
    workouts = await get_workouts()

    if not workouts:
        await message.answer("Список тренировок пуст. Попробуйте позже.")
        return

    workout_inline_keyboard = generate_workout_inline_keyboard(workouts)
    await message.answer("Выберите тренировку", reply_markup=workout_inline_keyboard)
    await state.set_state(WorkoutForm.workout_choice)


@router.callback_query(WorkoutForm.workout_choice)
async def process_workout_choice(callback_query: CallbackQuery, state: FSMContext):
    eat_per_hour = callback_query.data
    if eat_per_hour is None or not eat_per_hour.isdigit():
        await callback_query.message.answer("Некорректный выбор тренировки.")
        await callback_query.answer()
        return

    await callback_query.message.edit_reply_markup(None)
    await callback_query.message.answer("Сколько минут длилась тренировка?")

    await state.update_data(eat_per_hour=int(eat_per_hour))
    await state.set_state(WorkoutForm.duration)
    await callback_query.answer()


@router.message(WorkoutForm.duration)
async def process_workout_duration(message: Message, state: FSMContext):
    duration_text = message.text
    if duration_text is None or not duration_text.isdigit():
        await message.answer("Пожалуйста, введите длительность в минутах (положительное число).")
        return

    duration = int(duration_text)
    if duration <= 0:
        await message.answer("Пожалуйста, введите длительность в минутах (положительное число).")
        return

    data = await state.get_data()
    eat_per_hour = data.get("eat_per_hour")
    if eat_per_hour is None:
        await message.answer("Не удалось определить тренировку. Попробуйте снова.")
        await state.clear()
        return

    total_kcal = int(eat_per_hour / 60 * duration)
    statistics_schema = StatisticsSchema(telegram_id=message.from_user.id,
                                         amount=total_kcal, action='workout')
    await add_statistics(statistics_schema.model_dump())

    await message.answer("Действие записано.")
    await state.clear()


@router.message(Command("check_progress"))
async def check_progress_handler(message: Message):
    water_results, kcal_results, workout_results = await get_progress_from_statistics(message.from_user.id)
    water_norm, kcal_norm = await get_user_norms(message.from_user.id)

    water_pct = int(water_results / water_norm * 100) if water_norm else 0
    kcal_pct = int(kcal_results / kcal_norm * 100) if kcal_norm else 0

    text = (
        "Ваш прогресс за сегодня:\n\n"
        f"Вода: {water_results} мл из {water_norm} мл ({water_pct}%)\n"
        f"Калории: {kcal_results} ккал из {kcal_norm} ккал ({kcal_pct}%)\n"
        f"Тренировки: {workout_results} ккал сожжено"
    )
    await message.answer(text)


@router.message(Command("get_cal_stats"))
async def get_cal_stats_handler(message: Message):
    week_stats = await get_last_7_days_stats(message.from_user.id)
    img_bytes = build_kcal_plot(week_stats)
    if img_bytes:
        photo = BufferedInputFile(img_bytes, filename="kcal.png")
        await message.answer_photo(photo, caption="Потребление калорий за последние 7 дней")
    else:
        # пока не работает
        await message.answer("Недостаточно данных для графика.")


@router.message(Command("get_water_stats"))
async def get_water_stats_handler(message: Message):
    week_stats = await get_last_7_days_stats(message.from_user.id)
    img_bytes = build_water_plot(week_stats)
    if img_bytes:
        photo = BufferedInputFile(img_bytes, filename="water.png")
        await message.answer_photo(photo, caption="Потребление воды за последние 7 дней")
    else:
        # пока не работает
        await message.answer("Недостаточно данных для графика.")


def setup_user_handlers(dp: Dispatcher):
    dp.include_router(router)
