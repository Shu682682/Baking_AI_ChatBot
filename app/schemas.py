from pydantic import BaseModel
from typing import List


class BakingAnswer(BaseModel):
    summary: str
    baking_note: str
    tips: List[str]

class Ingredient(BaseModel):
    name: str
    amount: float | int | str
    unit: str
    calories_per_unit: float = 0.0
    ingredient_calories: float = 0.0


class Recipe(BaseModel):
    recipe_id: str
    name: str
    servings: int
    ingredients: List[Ingredient]
    steps: List[str]


class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    recipe_name: str
    servings: int
    ingredients: List[Ingredient]
    steps: List[str]
    answer: str
    total_calories: float = 0.0
    calories_per_serving: float = 0.0