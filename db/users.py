from typing import Tuple
from datetime import date as dt_date

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import func

from db.session import AsyncSessionLocal
from models.user import User, Norm, Statistic


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


async def add_statistics(statistic_data: dict) -> None:
    async with AsyncSessionLocal() as session:
        statistic = Statistic(**statistic_data)
        session.add(statistic)
        await session.commit()


async def user_exists(telegram_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User.id).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none() is not None


async def get_user_norms(telegram_id: int) -> Tuple[int, int]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Norm.water_norm, Norm.kcal_norm)
            .join(User, User.id == Norm.user_id)
        )
        row = result.first()
        if row is None:
            return 0, 0
        water_norm, kcal_norm = row
        return water_norm, kcal_norm


async def get_progress_from_statistics(telegram_id: int) -> Tuple[int, int, int, ]:
    today = dt_date.today()

    async with AsyncSessionLocal() as session:
        water_results = await session.execute(
            select(func.coalesce(func.sum(Statistic.amount), 0)).where(
                Statistic.telegram_id == telegram_id,
                Statistic.date == today,
                Statistic.action == 'water',
            )
        )

        kcal_results = await session.execute(
            select(func.coalesce(func.sum(Statistic.amount), 0)).where(
                Statistic.telegram_id == telegram_id,
                Statistic.date == today,
                Statistic.action == 'food')
        )

        workout_results = await session.execute(
            select(func.coalesce(func.sum(Statistic.amount), 0)).where(
                Statistic.telegram_id == telegram_id,
                Statistic.date == today,
                Statistic.action == 'workout')
        )

        return water_results.scalar_one(), kcal_results.scalar_one(), workout_results.scalar_one()
