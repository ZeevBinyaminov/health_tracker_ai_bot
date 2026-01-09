from typing import List

from sqlalchemy import select

from db.session import AsyncSessionLocal
from models.services import Workout


async def get_workouts(limit: int = 5) -> List[Workout]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Workout).order_by(Workout.id).limit(limit)
        )
        return list(result.scalars().all())
