from datetime import date as dt_date
from typing import List

from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(nullable=False, unique=True)
    name: Mapped[str] = mapped_column(nullable=False)
    weight: Mapped[int] = mapped_column(nullable=False)
    sex: Mapped[str] = mapped_column(nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    height: Mapped[int] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)
    day_activity: Mapped[int] = mapped_column(nullable=False)

    norm: Mapped["Norm"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False
    )
    statistics: Mapped[List["Statistic"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Norm(Base):
    __tablename__ = "norms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, unique=True
    )
    kcal_norm: Mapped[int] = mapped_column(nullable=False)
    water_norm: Mapped[int] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship(back_populates="norm")


class Statistic(Base):
    __tablename__ = "statistics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False)
    kcal_change: Mapped[int] = mapped_column(nullable=False)
    action: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[dt_date] = mapped_column(Date, nullable=False)

    user: Mapped["User"] = relationship(back_populates="statistics")
