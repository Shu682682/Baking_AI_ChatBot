import requests

OLLAMA_URL = "http://localhost:11434/api/chat"


def ask_ollama(system_prompt: str, user_prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "gemma3",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False
        },
        timeout=60
    )
    response.raise_for_status()
    data = response.json()
    return data["message"]["content"]