from pydantic import BaseModel
from typing import List
from pydantic import BaseModel
from typing import List

class BakingAnswer(BaseModel):
    summary: str
    baking_note: str
    tips: List[str]


class Ingredient(BaseModel):
    name: str
    amount: float
    unit: str


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