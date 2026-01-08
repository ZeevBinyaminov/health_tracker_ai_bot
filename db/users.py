from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.session import AsyncSessionLocal
from models.user import User, Norm


async def upsert_user_profile(profile_data: dict, norms_data: dict) -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User)
            .options(selectinload(User.norm))
            .where(User.telegram_id == profile_data["telegram_id"])
        )
        user = result.scalars().first()
        if user is None:
            user = User(**profile_data)
            user.norm = Norm(**norms_data)
            session.add(user)
        else:
            for field, value in profile_data.items():
                setattr(user, field, value)

            for field, value in norms_data.items():
                setattr(user.norm, field, value)

        await session.commit()
