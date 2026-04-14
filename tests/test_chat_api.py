from fastapi.testclient import TestClient
from app.main import app


def test_root():
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Baking AI Chatbot API is running"


def test_chat_endpoint(monkeypatch):
    from app import main
    from app.schemas import Recipe, Ingredient

    fake_recipe = Recipe(
        recipe_id="brownie_001",
        name="Classic Brownies",
        servings=12,
        ingredients=[
            Ingredient(name="butter", amount=153.33, unit="g"),
            Ingredient(name="sugar", amount=266.67, unit="g")
        ],
        steps=["Mix batter.", "Bake for 25 minutes."]
    )

    def fake_generate_response(message: str):
        return {
            "recipe": fake_recipe,
            "answer": "Mock brownie answer"
        }

    monkeypatch.setattr(main, "generate_response", fake_generate_response)

    client = TestClient(app)
    response = client.post("/chat", json={"message": "Give me a brownie recipe for 12 people"})

    assert response.status_code == 200

    data = response.json()
    assert data["recipe_name"] == "Classic Brownies"
    assert data["servings"] == 12
    assert len(data["ingredients"]) == 2
    assert data["answer"] == "Mock brownie answer"