import re
from app.schemas import Recipe, Ingredient
from app.prompts import BAKING_SYSTEM_PROMPT
from app.schemas import Recipe
from app.scaling import scale_recipe
from app.langchain_service import ask_with_langchain
from app.retrieval import find_recipe
from app.nutrition import calculate_total_calories, calculate_calories_per_serving
from app.nutrition import CALORIE_MAP, calculate_total_calories, calculate_calories_per_serving

def contains_chinese(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def extract_servings(user_message: str, default_servings: int) -> int:
    msg = user_message.lower()

    patterns = [
        r"(\d+)\s*人份",
        r"(\d+)\s*個人",
        r"(\d+)\s*个人",
        r"(\d+)\s*人",
        r"(\d+)\s*位",
        r"for\s+(\d+)\s+people",
        r"make\s+(\d+)\s+people",
        r"for\s+(\d+)",
        r"serves?\s+(\d+)",
        r"(\d+)\s*servings?",
        r"(\d+)\s+people"
    ]

    for pattern in patterns:
        match = re.search(pattern, msg)
        if match:
            return int(match.group(1))

    fallback = re.search(r"(\d+)", msg)
    if fallback:
        return int(fallback.group(1))

    return default_servings


def format_recipe_for_prompt(recipe: Recipe) -> str:
    ingredients_text = "\n".join(
        [f"- {ing.name}: {ing.amount} {ing.unit}".strip() for ing in recipe.ingredients]
    )
    steps_text = "\n".join(
        [f"{i + 1}. {step}" for i, step in enumerate(recipe.steps)]
    )

    return f"""
Recipe name: {recipe.name}
Servings: {recipe.servings}

Ingredients:
{ingredients_text}

Steps:
{steps_text}
""".strip()


def extract_constraints(user_message: str) -> dict:
    msg = user_message.lower()

    return {
        "no_nuts": "不要堅果" in user_message or "no nuts" in msg,
        "low_sugar": "低糖" in user_message or "low sugar" in msg,
        "no_dairy": "不要奶" in user_message or "dairy free" in msg or "no dairy" in msg,
        "no_egg": "不要蛋" in user_message or "egg free" in msg or "no egg" in msg,
        "air_fryer_only": "氣炸鍋" in user_message or "air fryer" in msg
    }


def format_constraints_for_prompt(constraints: dict) -> str:
    active_constraints = []

    if constraints["no_nuts"]:
        active_constraints.append("- Nut-free")
    if constraints["low_sugar"]:
        active_constraints.append("- Low sugar")
    if constraints["no_dairy"]:
        active_constraints.append("- Dairy-free")
    if constraints["no_egg"]:
        active_constraints.append("- Egg-free")
    if constraints["air_fryer_only"]:
        active_constraints.append("- Air fryer only")

    if not active_constraints:
        return "No special dietary or equipment constraints."

    return "\n".join(active_constraints)


def extract_steps_from_answer(answer: str) -> list[str]:
    lines = [line.strip() for line in answer.splitlines() if line.strip()]
    steps = []
    in_steps = False

    for line in lines:
        if line in {"步驟：", "做法：", "Steps:", "Instructions:"}:
            in_steps = True
            continue

        if in_steps:
            if re.match(r"^\d+[\.\)]\s*", line):
                step_text = re.sub(r"^\d+[\.\)]\s*", "", line)
                steps.append(step_text)
            elif line.startswith("- "):
                steps.append(line[2:])
            elif line.startswith("烘焙小提醒") or line.startswith("Baking Note"):
                break

    return steps


def enrich_recipe_with_calories(recipe: Recipe) -> Recipe:
    enriched_ingredients = []

    for ing in recipe.ingredients:
        key = (ing.name.strip().lower(), ing.unit.strip().lower())
        calories_per_unit = CALORIE_MAP.get(key, 0.0)

        if isinstance(ing.amount, (int, float)):
            ingredient_calories = round(ing.amount * calories_per_unit, 2)
        else:
            ingredient_calories = 0.0

        enriched_ingredients.append(
            Ingredient(
                name=ing.name,
                amount=ing.amount,
                unit=ing.unit,
                calories_per_unit=calories_per_unit,
                ingredient_calories=ingredient_calories
            )
        )

    return Recipe(
        recipe_id=recipe.recipe_id,
        name=recipe.name,
        servings=recipe.servings,
        ingredients=enriched_ingredients,
        steps=recipe.steps
    )

def generate_response(user_message: str) -> dict:
    recipe = find_recipe(user_message, use_chroma=True)

    if recipe is None:
        if contains_chinese(user_message):
            return {
                "recipe": None,
                "translated_steps": [],
                "answer": "抱歉，我目前找不到這道甜點的食譜。請試試其他甜點名稱，例如南瓜派、布朗尼或提拉米蘇。",
                "total_calories": 0.0,
                "calories_per_serving": 0.0
            }
        return {
            "recipe": None,
            "translated_steps": [],
            "answer": "Sorry, I couldn't find a recipe for that dessert. Please try another dessert name such as pumpkin pie, brownies, or tiramisu.",
            "total_calories": 0.0,
            "calories_per_serving": 0.0
        }

    target_servings = extract_servings(user_message, recipe.servings)
    scaled_recipe = scale_recipe(recipe, target_servings)
    scaled_recipe = enrich_recipe_with_calories(scaled_recipe)

    total_calories = calculate_total_calories(scaled_recipe)
    calories_per_serving = calculate_calories_per_serving(scaled_recipe)

    constraints = extract_constraints(user_message)
    is_chinese_input = contains_chinese(user_message)

    system_prompt = BAKING_SYSTEM_PROMPT
    user_prompt = f"""
User request:
{user_message}

Recipe data:
{format_recipe_for_prompt(scaled_recipe)}

Nutrition:
- Total calories: {total_calories} kcal
- Calories per serving: {calories_per_serving} kcal

Constraints:
{format_constraints_for_prompt(constraints)}

Instructions:
- Final output language must always match the user's input language.
- If the user writes in English, respond only in English.
- If the user writes in Chinese, respond only in Traditional Chinese.
- Do not include pinyin.
- Do not provide bilingual output.
- Do not rewrite the full recipe.
- Only provide:
  1. one short summary sentence
  2. one short baking note
  3. one optional tip
""".strip()

    answer = ask_with_langchain(system_prompt, user_prompt)

    if is_chinese_input:
        translated_steps = extract_steps_from_answer(answer)
    else:
        translated_steps = scaled_recipe.steps

    return {
        "recipe": scaled_recipe,
        "translated_steps": translated_steps,
        "answer": answer,
        "total_calories": total_calories,
        "calories_per_serving": calories_per_serving
    }