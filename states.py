from aiogram.fsm.state import State, StatesGroup


class ProfileForm(StatesGroup):
    name = State()
    weight = State()
    age = State()
    sex = State()
    height = State()
    city = State()
    day_activity = State()
    kcal_norm = State()


class FoodForm(StatesGroup):
    food_name = State()
    food_choice = State()
    amount = State()


class WaterForm(StatesGroup):
    amount = State()


class WorkoutForm(StatesGroup):
    workout_choice = State()
    duration = State()
