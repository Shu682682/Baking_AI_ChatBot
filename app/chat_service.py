import re

from app.prompts import BAKING_SYSTEM_PROMPT
from app.schemas import Recipe
from app.scaling import scale_recipe
from app.langchain_service import ask_with_langchain
from app.retrieval import find_recipe


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
        [f"- {ing.name}: {ing.amount} {ing.unit}" for ing in recipe.ingredients]
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


def generate_response(user_message: str) -> dict:
    recipe = find_recipe(user_message, use_chroma=True)

    target_servings = extract_servings(user_message, recipe.servings)
    scaled_recipe = scale_recipe(recipe, target_servings)

    system_prompt = BAKING_SYSTEM_PROMPT
    user_prompt = f"""
User request: {user_message}

Recipe data:
{format_recipe_for_prompt(scaled_recipe)}
""".strip()

    answer = ask_with_langchain(system_prompt, user_prompt)

    return {
        "recipe": scaled_recipe,
        "answer": answer
    }