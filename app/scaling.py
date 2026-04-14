from app.schemas import Recipe, Ingredient


def scale_recipe(recipe: Recipe, target_servings: int) -> Recipe:
    scale = target_servings / recipe.servings

    scaled_ingredients = []
    for ing in recipe.ingredients:
        scaled_ingredients.append(
            Ingredient(
                name=ing.name,
                amount=round(ing.amount * scale, 2),
                unit=ing.unit
            )
        )

    return Recipe(
        recipe_id=recipe.recipe_id,
        name=recipe.name,
        servings=target_servings,
        ingredients=scaled_ingredients,
        steps=recipe.steps
    )