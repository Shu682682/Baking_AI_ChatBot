from app.schemas import Recipe, Ingredient
from app.scaling import scale_recipe


def test_scale_recipe():
    recipe = Recipe(
        recipe_id="1",
        name="Test Cake",
        servings=4,
        ingredients=[
            Ingredient(name="flour", amount=100, unit="g"),
            Ingredient(name="egg", amount=1, unit="pcs")
        ],
        steps=["Mix", "Bake"]
    )

    scaled = scale_recipe(recipe, 8)

    assert scaled.servings == 8
    assert scaled.ingredients[0].amount == 200
    assert scaled.ingredients[1].amount == 2