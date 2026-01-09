from sqlalchemy import select

from db.session import AsyncSessionLocal
from models.services import Workout


# EAT — калории, сжигаемые за час тренировки.
WORKOUTS = [
    {"name": "Бег", "min_degrees": 20, "EAT": 600},
    {"name": "Велосипед", "min_degrees": 15, "EAT": 500},
    {"name": "Плавание", "min_degrees": 25, "EAT": 700},
    {"name": "Ходьба", "min_degrees": 10, "EAT": 250},
    {"name": "Силовая тренировка", "min_degrees": 18, "EAT": 400},
]


async def seed_workouts() -> None:
    async with AsyncSessionLocal() as session:
        for item in WORKOUTS:
            result = await session.execute(
                select(Workout).where(Workout.name == item["name"])
            )
            exists = result.scalars().first()
            if exists:
                continue
            session.add(Workout(**item))
        await session.commit()
