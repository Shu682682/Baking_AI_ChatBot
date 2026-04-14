from langchain_ollama import OllamaEmbeddings

embedding_model = OllamaEmbeddings(model="embeddinggemma")

def embed_texts(texts: list[str]) -> list[list[float]]:
    return embedding_model.embed_documents(texts)

def embed_query(text: str) -> list[float]:
    return embedding_model.embed_query(text)