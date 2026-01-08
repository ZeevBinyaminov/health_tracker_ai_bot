from datetime import date

from pydantic import BaseModel, ConfigDict


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


class Statistics(BaseModel):
    user_id: int
    kcal_change: int
    action: str
    date: date
