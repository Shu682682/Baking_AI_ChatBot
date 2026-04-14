from app.retrieval import find_recipe_by_keyword
from app.schemas import Recipe, Ingredient

from app.retrieval import find_recipe

def test_find_recipe_keyword_mode():
    recipe = find_recipe("I want brownie", use_chroma=False)
    assert recipe.name == "Classic Brownies"

def test_find_recipe_by_keyword():
    recipes = [
        Recipe(
            recipe_id="1",
            name="Classic Chocolate Cake",
            servings=8,
            ingredients=[Ingredient(name="flour", amount=100, unit="g")],
            steps=["Mix"]
        ),
        Recipe(
            recipe_id="2",
            name="Vanilla Cupcakes",
            servings=12,
            ingredients=[Ingredient(name="flour", amount=100, unit="g")],
            steps=["Mix"]
        )
    ]

    result = find_recipe_by_keyword(recipes, "I want chocolate cake")
    assert result.name == "Classic Chocolate Cake"
    
def make_recipe(recipe_id: str, name: str, servings: int) -> Recipe:
    return Recipe(
        recipe_id=recipe_id,
        name=name,
        servings=servings,
        ingredients=[Ingredient(name="flour", amount=100, unit="g")],
        steps=["Mix", "Bake"]
    )


def test_find_chocolate_cake():
    recipes = [
        make_recipe("1", "Classic Chocolate Cake", 8),
        make_recipe("2", "Vanilla Cupcakes", 12),
        make_recipe("3", "Pumpkin Pie", 8),
    ]

    result = find_recipe_by_keyword(recipes, "I want to make 20 people chocolate cake")
    assert result.name == "Classic Chocolate Cake"


def test_find_pumpkin_pie():
    recipes = [
        make_recipe("1", "Classic Chocolate Cake", 8),
        make_recipe("2", "Vanilla Cupcakes", 12),
        make_recipe("3", "Pumpkin Pie", 8),
    ]

    result = find_recipe_by_keyword(recipes, "I want pumpkin pie")
    assert result.name == "Pumpkin Pie"
    
def test_find_tiramisu():
    recipes=[
        make_recipe("1", "Tiramisu",6),
        make_recipe("3", "Pumpkin Pie", 8),
         make_recipe("2", "Vanilla Cupcakes", 12),
                    
    ]
    result=find_recipe_by_keyword(recipes, "I want tiramisu")
    assert result.name=="Tiramisu"