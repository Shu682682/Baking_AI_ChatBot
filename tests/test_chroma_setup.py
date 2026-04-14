from app.chroma_setup import recipe_to_document, recipe_to_metadata


def test_recipe_to_document_contains_key_fields():
    recipe = {
        "recipe_id": "pumpkin_pie_001",
        "name": "Pumpkin Pie",
        "servings": 8,
        "ingredients": [
            {"name": "pumpkin puree", "amount": 425, "unit": "g"},
            {"name": "eggs", "amount": 2, "unit": "pcs"}
        ],
        "steps": ["Mix ingredients.", "Bake in pie crust."],
        "tags": ["pie", "pumpkin"],
        "equipment": ["oven", "pie-dish"],
        "allergens": ["egg", "milk"]
    }

    doc = recipe_to_document(recipe)

    assert "Pumpkin Pie" in doc
    assert "Servings: 8" in doc
    assert "pumpkin puree 425g" in doc
    assert "Tags: pie, pumpkin." in doc
    assert "Equipment: oven, pie-dish." in doc


def test_recipe_to_metadata():
    recipe = {
        "recipe_id": "pumpkin_pie_001",
        "name": "Pumpkin Pie",
        "servings": 8
    }

    metadata = recipe_to_metadata(recipe)

    assert metadata["recipe_id"] == "pumpkin_pie_001"
    assert metadata["name"] == "Pumpkin Pie"
    assert metadata["servings"] == 8
    assert metadata["category"] == "dessert"