from pydantic import BaseModel, ConfigDict


class Workout(BaseModel):
    id: int
    name: str
    min_degrees: int
    EAT: int

    model_config = ConfigDict(from_attributes=True)


# пока не используется
class Food(BaseModel):
    id: int
    name: str
    amount: int
    unit: str
    calories: int
    fat: int
    carbs: int
    protein: int

    model_config = ConfigDict(from_attributes=True)
