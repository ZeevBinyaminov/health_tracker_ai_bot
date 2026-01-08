from aiogram import Router, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from states import ProfileForm
from keyboards.user_keyboards import sex_choice_keyboard

from schemas.user import UserSchema, NormsSchema
from db.users import upsert_user_profile

from ext_api.weathermap_api import get_weather_data

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Доступные команды:\n"
        "/start - Начало работы\n"
        "/set_profile - заполнить профиль\n"
        "/log_water - записать потребление воды\n"
        "/log_food - записать потребление пищи\n"
        "/log_workout - записать тренировку\n"
        "/check_progress - посмотреть статистику\n"
    )


@router.message(Command("set_profile"))
async def start_profile_form(message: Message, state: FSMContext):
    await message.answer("Давайте заполним Ваш профиль! Как Вас зовут?")
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
async def process_sex(callback_query, state: FSMContext):
    sex = callback_query.data
    await state.update_data(sex=sex)
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
    additional_for_activity = 500 * int(60/day_activity)
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

    await message.answer(f"Профиль заполнен!")

    await state.clear()


def setup_user_handlers(dp: Dispatcher):
    dp.include_router(router)
