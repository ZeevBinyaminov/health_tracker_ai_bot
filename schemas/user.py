from datetime import date as dt_date

from pydantic import BaseModel, ConfigDict, Field


class UserSchema(BaseModel):
    telegram_id: int
    name: str
    weight: int
    age: int
    height: int
    sex: str
    city: str
    day_activity: int

    model_config = ConfigDict(from_attributes=True)


class NormsSchema(BaseModel):
    kcal_norm: int
    water_norm: int


class StatisticsSchema(BaseModel):
    telegram_id: int
    amount: int
    action: str
    date: dt_date = Field(default_factory=dt_date.today)
