from google import genai

from .config import (
    GEMINI_API_KEY,
    EMBEDDING_MODEL
)


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def embed_text(text):
    """
    Generate one embedding vector.
    """

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text
    )

    return response.embeddings[0].values


def embed_documents(texts):
    """
    Generate embeddings for multiple texts.
    """

    embeddings = []

    for text in texts:

        embedding = embed_text(text)

        embeddings.append(embedding)

    return embeddings

