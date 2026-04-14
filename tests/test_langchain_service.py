from app import langchain_service


class FakeResponse:
    def __init__(self, content):
        self.content = content


class FakeLLM:
    def invoke(self, messages):
        return FakeResponse("This is a fake baking answer.")


def test_ask_with_langchain(monkeypatch):
    monkeypatch.setattr(langchain_service, "llm", FakeLLM())

    answer = langchain_service.ask_with_langchain(
        "You are a baking assistant.",
        "Give me a brownie recipe."
    )

    assert answer == "This is a fake baking answer."