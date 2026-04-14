import json
from pathlib import Path

import pytest


@pytest.fixture
def sample_recipes():
    return [
        {
            "recipe_id": "choco_cake_001",
            "name": "Classic Chocolate Cake",
            "servings": 8,
            "ingredients": [
                {"name": "flour", "amount": 200, "unit": "g"},
                {"name": "sugar", "amount": 180, "unit": "g"},
                {"name": "eggs", "amount": 2, "unit": "pcs"}
            ],
            "steps": [
                "Mix ingredients.",
                "Bake for 30 minutes."
            ],
            "tags": ["cake", "chocolate"],
            "equipment": ["oven", "cake-pan"],
            "allergens": ["egg", "gluten"]
        },
        {
            "recipe_id": "pumpkin_pie_001",
            "name": "Pumpkin Pie",
            "servings": 8,
            "ingredients": [
                {"name": "pumpkin puree", "amount": 425, "unit": "g"},
                {"name": "eggs", "amount": 2, "unit": "pcs"},
                {"name": "milk", "amount": 350, "unit": "ml"}
            ],
            "steps": [
                "Mix ingredients.",
                "Bake in pie crust."
            ],
            "tags": ["pie", "pumpkin"],
            "equipment": ["oven", "pie-dish"],
            "allergens": ["egg", "milk"]
        },
        {
            "recipe_id": "brownie_001",
            "name": "Classic Brownies",
            "servings": 9,
            "ingredients": [
                {"name": "butter", "amount": 115, "unit": "g"},
                {"name": "sugar", "amount": 200, "unit": "g"},
                {"name": "flour", "amount": 95, "unit": "g"}
            ],
            "steps": [
                "Mix batter.",
                "Bake for 25 minutes."
            ],
            "tags": ["brownie", "chocolate"],
            "equipment": ["oven", "square-pan"],
            "allergens": ["gluten", "milk"]
        }
    ]


@pytest.fixture
def temp_recipe_file(tmp_path, sample_recipes):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    recipe_path = data_dir / "recipes.json"

    with open(recipe_path, "w", encoding="utf-8") as f:
        json.dump(sample_recipes, f, ensure_ascii=False, indent=2)

    return recipe_path