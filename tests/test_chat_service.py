from app.schemas import Recipe, Ingredient
from app import chat_service


def make_recipe():
    return Recipe(
        recipe_id="pumpkin_pie_001",
        name="Pumpkin Pie",
        servings=8,
        ingredients=[
            Ingredient(name="pumpkin puree", amount=425, unit="g"),
            Ingredient(name="eggs", amount=2, unit="pcs")
        ],
        steps=["Mix ingredients.", "Bake in pie crust."]
    )


def test_generate_response(monkeypatch):
    monkeypatch.setattr(chat_service, "find_recipe", lambda message, use_chroma=True: make_recipe())
    monkeypatch.setattr(chat_service, "ask_with_langchain", lambda system_prompt, user_prompt: "Mock AI answer")

    result = chat_service.generate_response("我要做南瓜派5個人")

    assert result["recipe"].name == "Pumpkin Pie"
    assert result["recipe"].servings == 5
    assert result["answer"] == "Mock AI answer"