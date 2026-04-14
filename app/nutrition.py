from app.schemas import Recipe

# 每個單位的熱量估算
# key: (ingredient_name_lower, unit_lower)
CALORIE_MAP = {
    ("all-purpose flour", "g"): 3.64,
    ("cake flour", "g"): 3.64,
    ("sugar", "g"): 3.87,
    ("brown sugar", "g"): 3.80,
    ("cocoa powder", "g"): 2.28,
    ("butter", "g"): 7.17,
    ("vegetable oil", "ml"): 8.0,
    ("milk", "ml"): 0.64,
    ("heavy cream", "ml"): 3.4,
    ("sour cream", "ml"): 1.9,
    ("buttermilk", "ml"): 0.6,
    ("evaporated milk", "ml"): 1.35,
    ("espresso", "ml"): 0.02,
    ("lemon juice", "ml"): 0.22,
    ("key lime juice", "ml"): 0.25,
    ("vanilla extract", "ml"): 2.88,
    ("corn syrup", "ml"): 3.1,

    ("eggs", "pcs"): 72.0,
    ("egg yolks", "pcs"): 55.0,
    ("bananas", "pcs"): 105.0,
    ("ripe bananas", "pcs"): 105.0,
    ("apples", "pcs"): 95.0,
    ("pie crust", "pcs"): 800.0,
    ("tart shell", "pcs"): 700.0,
    ("graham cracker crust", "pcs"): 960.0,
    ("shortcakes", "pcs"): 180.0,
    ("oreo cookies", "pcs"): 53.0,
    ("ladyfingers", "pcs"): 24.0,

    ("pumpkin puree", "g"): 0.34,
    ("mascarpone cheese", "g"): 4.35,
    ("cream cheese", "g"): 3.42,
    ("sweetened condensed milk", "g"): 3.21,
    ("graham cracker crumbs", "g"): 4.2,
    ("dark chocolate", "g"): 5.46,
    ("chocolate chips", "g"): 5.0,
    ("oreo cookies", "g"): 4.8,
    ("blueberries", "g"): 0.57,
    ("mixed berries", "g"): 0.5,
    ("strawberries", "g"): 0.32,
    ("peaches", "g"): 0.39,
    ("carrots", "g"): 0.41,
    ("pecans", "g"): 6.91,
    ("peanut butter", "g"): 5.88,
    ("cornstarch", "g"): 3.81,
    ("cinnamon", "g"): 2.47,
    ("matcha powder", "g"): 3.24,
    ("lime zest", "g"): 0.3,
    ("vanilla pudding mix", "g"): 3.6,
}


def get_ingredient_calories(name: str, amount: float | int | str, unit: str) -> float:
    if not isinstance(amount, (int, float)):
        return 0.0

    key = (name.strip().lower(), unit.strip().lower())
    calories_per_unit = CALORIE_MAP.get(key, 0.0)
    return round(amount * calories_per_unit, 2)


def calculate_total_calories(recipe: Recipe) -> float:
    total = 0.0

    for ing in recipe.ingredients:
        total += get_ingredient_calories(ing.name, ing.amount, ing.unit)

    return round(total, 2)


def calculate_calories_per_serving(recipe: Recipe) -> float:
    if recipe.servings <= 0:
        return 0.0

    total = calculate_total_calories(recipe)
    return round(total / recipe.servings, 2)