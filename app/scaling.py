from app.schemas import Recipe, Ingredient


def scale_recipe(recipe: Recipe, target_servings: int) -> Recipe:
    if recipe.servings <= 0:
        raise ValueError("recipe.servings must be greater than 0")

    scale = target_servings / recipe.servings

    scaled_ingredients = []
    for ing in recipe.ingredients:
        amount = ing.amount

        if isinstance(amount, (int, float)):
            scaled_amount = round(amount * scale, 2)
            if isinstance(scaled_amount, float) and scaled_amount.is_integer():
                scaled_amount = int(scaled_amount)
        else:
            scaled_amount = amount

        scaled_ingredients.append(
            Ingredient(
                name=ing.name,
                amount=scaled_amount,
                unit=ing.unit,
                calories_per_unit=ing.calories_per_unit
            )
        )

    return Recipe(
        recipe_id=recipe.recipe_id,
        name=recipe.name,
        servings=target_servings,
        ingredients=scaled_ingredients,
        steps=recipe.steps
    )