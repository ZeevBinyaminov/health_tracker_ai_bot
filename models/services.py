from datetime import date
from typing import List

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    min_degrees: Mapped[int] = mapped_column(nullable=False)
    EAT: Mapped[int] = mapped_column(nullable=False)


# пока не используется
class Food(Base):
    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    amount: Mapped[int] = mapped_column(nullable=False)
    unit: Mapped[str] = mapped_column(nullable=False)
    calories: Mapped[int] = mapped_column(nullable=False)
    fat: Mapped[int] = mapped_column(nullable=False)
    carbs: Mapped[int] = mapped_column(nullable=False)
    protein: Mapped[int] = mapped_column(nullable=False)
