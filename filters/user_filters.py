from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db.users import user_exists
from states import ProfileForm


class RegisteredUserFilter(BaseFilter):
    async def __call__(
        self,
        event: Message | CallbackQuery,
        state: FSMContext | None = None,
    ) -> bool:
        if isinstance(event, Message):
            text = event.text or ""
            cmd = text.split(maxsplit=1)[0]
            if cmd in ("/start", "/set_profile", "/help"):
                return True

        if state is not None:
            current_state = await state.get_state()
            if current_state and current_state.startswith(f"{ProfileForm.__name__}:"):
                return True

        if isinstance(event, CallbackQuery) and event.data == "cancel":
            return True

        is_registered = await user_exists(event.from_user.id)
        if not is_registered:
            if isinstance(event, CallbackQuery):
                await event.message.answer(
                    "Введите /set_profile, чтобы открыть доступ к функционалу приложения."
                )
                await event.answer()
            else:
                await event.answer(
                    "Введите /set_profile, чтобы открыть доступ к функционалу приложения."
                )
        return is_registered
