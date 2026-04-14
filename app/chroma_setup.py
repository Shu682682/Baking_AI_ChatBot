import json
from pathlib import Path
from typing import Any

import chromadb

from app.embedding_service import embed_texts

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "recipes.json"
CHROMA_PATH = str(BASE_DIR / "chroma_db")
COLLECTION_NAME = "recipes"


def load_recipe_dicts() -> list[dict[str, Any]]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def recipe_to_document(recipe: dict[str, Any]) -> str:
    ingredients = ", ".join(
        f"{ing['name']} {ing['amount']}{ing['unit']}"
        for ing in recipe.get("ingredients", [])
    )

    steps = " ".join(recipe.get("steps", []))
    tags = ", ".join(recipe.get("tags", []))
    equipment = ", ".join(recipe.get("equipment", []))
    allergens = ", ".join(recipe.get("allergens", []))

    parts = [
        f"Recipe name: {recipe.get('name', '')}.",
        f"Servings: {recipe.get('servings', '')}.",
        f"Ingredients: {ingredients}.",
        f"Steps: {steps}.",
    ]

    if tags:
        parts.append(f"Tags: {tags}.")
    if equipment:
        parts.append(f"Equipment: {equipment}.")
    if allergens:
        parts.append(f"Allergens: {allergens}.")
    if recipe.get("notes"):
        parts.append(f"Notes: {recipe['notes']}.")

    return " ".join(parts).strip()


def recipe_to_metadata(recipe: dict[str, Any]) -> dict[str, Any]:
    return {
        "recipe_id": recipe["recipe_id"],
        "name": recipe["name"],
        "servings": recipe["servings"],
        "category": "dessert"
    }


def rebuild_chroma_collection() -> None:
    recipes = load_recipe_dicts()

    if not recipes:
        raise ValueError("No recipes found in data/recipes.json")

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    existing = client.list_collections()
    existing_names = [c.name if hasattr(c, "name") else c for c in existing]
    if COLLECTION_NAME in existing_names:
        client.delete_collection(COLLECTION_NAME)

    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    ids = []
    documents = []
    metadatas = []

    for recipe in recipes:
        ids.append(recipe["recipe_id"])
        documents.append(recipe_to_document(recipe))
        metadatas.append(recipe_to_metadata(recipe))

    embeddings = embed_texts(documents)

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    print(f"Built Chroma collection '{COLLECTION_NAME}' with {len(ids)} recipes.")


if __name__ == "__main__":
    rebuild_chroma_collection()