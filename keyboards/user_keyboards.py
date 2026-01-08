from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

sex_choice_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Мужчина", callback_data="man")],
        [InlineKeyboardButton(text="Женщина", callback_data="woman")],
    ]
)
