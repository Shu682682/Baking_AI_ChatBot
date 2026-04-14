from pathlib import Path
import json
import chromadb

from app.schemas import Recipe

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "recipes.json"
CHROMA_PATH = str(BASE_DIR / "chroma_db")
COLLECTION_NAME = "recipes"

RECIPE_KEYWORDS = {
    "Classic Chocolate Cake": [
        "chocolate cake", "choco cake", "classic chocolate cake", "巧克力蛋糕"
    ],
    "Vanilla Cupcakes": [
        "vanilla cupcake", "vanilla cupcakes", "cupcake", "cupcakes", "香草杯子蛋糕", "杯子蛋糕"
    ],
    "Classic Brownies": [
        "brownie", "brownies", "布朗尼"
    ],
    "Classic Tiramisu": [
        "tiramisu", "提拉米蘇", "提拉米苏","Tiramisu Cake"
    ],
    "Matcha Cake": [
        "matcha cake", "green tea cake", "抹茶蛋糕"
    ],
    "Mixed Fruit Pie": [
        "fruit pie", "mixed fruit pie", "berry pie", "水果派"
    ],
    "New York Cheesecake": [
        "new york cheesecake", "ny cheesecake", "cheesecake", "起司蛋糕", "乳酪蛋糕", "紐約起司蛋糕"
    ],
    "Chocolate Tart": [
        "chocolate tart", "tart", "巧克力塔", "chocolate pie"
    ],
    "Classic Lemon Cake": [
        "lemon cake", "classic lemon cake", "檸檬蛋糕"
    ],
    "Banana Cream Pie": [
        "banana cream pie", "香蕉奶油派","banana pie"
    ],
    "Oreo Chocolate Cake": [
        "oreo chocolate cake", "oreo cake", "oreo巧克力蛋糕", "oreo蛋糕"
    ],
    "Blueberry Muffins": [
        "blueberry muffin", "blueberry muffins", "muffin", "muffins", "藍莓瑪芬", "玛芬"
    ],
    "Pumpkin Pie": [
        "pumpkin pie", "南瓜派"
    ],
    "Apple Pie": [
        "apple pie", "蘋果派"
    ],
    "Pecan Pie": [
        "pecan pie", "胡桃派"
    ],
    "Red Velvet Cake": [
        "red velvet cake", "red velvet", "紅絲絨蛋糕", "红丝绒蛋糕"
    ],
    "Carrot Cake": [
        "carrot cake", "胡蘿蔔蛋糕", "胡萝卜蛋糕"
    ],
    "Cheesecake Bars": [
        "cheesecake bars", "cheese bars", "起司條", "乳酪條"
    ],
    "Chocolate Chip Cookies": [
        "chocolate chip cookie", "chocolate chip cookies", "cookies", "cookie", "巧克力豆餅乾", "巧克力豆饼干"
    ],
    "Snickerdoodles": [
        "snickerdoodle", "snickerdoodles"
    ],
    "Sugar Cookies": [
        "sugar cookie", "sugar cookies", "糖霜餅乾", "糖餅乾"
    ],
    "Banana Bread": [
        "banana bread", "香蕉麵包", "香蕉面包"
    ],
    "Lemon Bars": [
        "lemon bar", "lemon bars", "檸檬條", "柠檬条"
    ],
    "Peach Cobbler": [
        "peach cobbler", "桃子 cobbler", "蜜桃 cobbler"
    ],
    "Strawberry Shortcake": [
        "strawberry shortcake", "草莓蛋糕", "草莓鮮奶油蛋糕", "strawberry cake", "Strawberry"
    ],
    "Key Lime Pie": [
        "key lime pie", "lime pie", "青檸派", "酸橙派"
    ],
    "Whoopie Pies": [
        "whoopie pie", "whoopie pies"
    ],
    "Boston Cream Pie": [
        "boston cream pie", "波士頓奶油派", "波士顿奶油派", "Boston pie"
    ],
    "Coffee Cake": [
        "coffee cake", "咖啡蛋糕"
    ],
    "Pound Cake": [
        "pound cake", "磅蛋糕"
    ],
    "Cinnamon Rolls": [
        "cinnamon roll", "cinnamon rolls", "肉桂捲", "肉桂卷","cinnamon buns"
    ],
    "Glazed Donuts": [
        "glazed donut", "glazed donuts", "donut", "donuts", "doughnut", "doughnuts", "甜甜圈"
    ],
    "Red Velvet Cupcakes": [
        "red velvet cupcake", "red velvet cupcakes", "紅絲絨杯子蛋糕", "红丝绒杯子蛋糕"
    ],
    "Molten Lava Cake": [
        "molten lava cake", "lava cake", "熔岩巧克力蛋糕"
    ],
    "Peanut Butter Cookies": [
        "peanut butter cookie", "peanut butter cookies", "花生醬餅乾", "花生酱饼干"
    ]
}
def load_recipes() -> list[Recipe]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"recipes.json not found at: {DATA_PATH}")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [Recipe(**item) for item in data]


def find_recipe_by_id(recipe_id: str, recipes: list[Recipe]) -> Recipe:
    for recipe in recipes:
        if recipe.recipe_id == recipe_id:
            return recipe
    return recipes[0]


def normalize_text(text: str) -> str:
    return " ".join(text.lower().strip().split())


def build_recipe_alias_map(recipes: list[Recipe]) -> dict[str, list[str]]:
    alias_map: dict[str, list[str]] = {}

    for recipe in recipes:
        aliases = [recipe.name.lower()]
        if recipe.name in RECIPE_KEYWORDS:
            aliases.extend([a.lower() for a in RECIPE_KEYWORDS[recipe.name]])
        alias_map[recipe.name] = list(set(aliases))

    return alias_map


def find_recipe_by_keyword(recipes: list[Recipe], user_message: str) -> Recipe | None:
    if not recipes:
        raise ValueError("recipes list is empty")

    normalized_message = normalize_text(user_message)
    alias_map = build_recipe_alias_map(recipes)

    best_recipe = None
    best_score = 0

    for recipe in recipes:
        score = 0
        recipe_name_lower = recipe.name.lower()

        if recipe_name_lower in normalized_message:
            score += 10

        for alias in alias_map.get(recipe.name, []):
            if alias in normalized_message:
                score += max(3, len(alias.split()))

        recipe_tokens = recipe_name_lower.replace("-", " ").split()
        for token in recipe_tokens:
            if token in normalized_message:
                score += 1

        if score > best_score:
            best_score = score
            best_recipe = recipe

    return best_recipe



def find_recipe(user_message: str, use_chroma: bool = False) -> Recipe:
    recipes = load_recipes()
    normalized_message = normalize_text(user_message)
    alias_map = build_recipe_alias_map(recipes)

    # First, try to match exact aliases
    for recipe in recipes:
        for alias in alias_map.get(recipe.name, []):
            if alias in normalized_message:
                return recipe

    # Second, keyword scoring
    keyword_recipe = find_recipe_by_keyword(recipes, user_message)

    if keyword_recipe is not None:
        return keyword_recipe

    # Finally, use chroma
    if use_chroma:
        try:
            return find_recipe_by_chroma(user_message)
        except Exception:
            pass

    #  fallback
    return recipes[0]

def find_recipe_by_chroma(user_message: str) -> Recipe:
    recipes = load_recipes()

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    from app.embedding_service import embed_query
    query_vector = embed_query(user_message)

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=1
    )

    ids = results.get("ids", [])
    if not ids or not ids[0]:
        return recipes[0]

    recipe_id = ids[0][0]
    return find_recipe_by_id(recipe_id, recipes)

# def find_recipe_by_chroma(user_message: str) -> Recipe:
#     recipes = load_recipes()
#     client = chromadb.PersistentClient(path=CHROMA_PATH)
#     collection = client.get_or_create_collection(name=COLLECTION_NAME)

#     query_vector = embed_query(user_message)

#     results = collection.query(
#         query_embeddings=[query_vector],
#         n_results=1
#     )

#     ids = results.get("ids", [])
#     if not ids or not ids[0]:
#         return recipes[0]

#     recipe_id = ids[0][0]
#     return find_recipe_by_id(recipe_id, recipes)