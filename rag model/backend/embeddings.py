from google import genai

from backend.config import (
    GEMINI_API_KEY,
    EMBEDDING_MODEL
)


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def create_embedding(text):

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text
    )

    return response.embeddings[0].values