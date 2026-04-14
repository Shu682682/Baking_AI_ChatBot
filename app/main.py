from fastapi import FastAPI
from app.schemas import ChatRequest, ChatResponse
from app.chat_service import generate_response

app = FastAPI(title="Baking AI Chatbot")


@app.get("/")
def root():
    return {"message": "Baking AI Chatbot API is running"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = generate_response(req.message)
    recipe = result["recipe"]

    return ChatResponse(
        recipe_name=recipe.name,
        servings=recipe.servings,
        ingredients=recipe.ingredients,
        steps=recipe.steps,
        answer=result["answer"]
    )