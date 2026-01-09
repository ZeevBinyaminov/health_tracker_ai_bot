from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ext_api.fatsecret_api import Food
from models.services import Workout


sex_choice_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Мужчина", callback_data="man"),
         InlineKeyboardButton(text="Женщина", callback_data="woman")],
    ]
)


def generate_food_inline_keyboard(foods: List[Food], max_items: int = 5) -> InlineKeyboardMarkup:
    if not foods:
        return InlineKeyboardMarkup(inline_keyboard=[])

    keyboard = []
    for index, food in enumerate(foods[:max_items]):
        button_text = f"{food.name} ({int(food.calories)} ккал на 100 грамм)"
        keyboard.append(
            [InlineKeyboardButton(
                text=button_text, callback_data=f"{food.calories}")]
        )

    keyboard.append([InlineKeyboardButton(
        text="Отменить", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def generate_workout_inline_keyboard(workouts: List[Workout], max_items: int = 5) -> InlineKeyboardMarkup:
    if not workouts:
        return InlineKeyboardMarkup(inline_keyboard=[])

    keyboard = []
    for workout in workouts[:max_items]:
        button_text = f"{workout.name} ({workout.EAT} ккал/час)"
        keyboard.append(
            [InlineKeyboardButton(
                text=button_text, callback_data=f"{workout.EAT}")]
        )

    keyboard.append([InlineKeyboardButton(
        text="Отменить", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
