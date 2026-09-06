from google import genai

from .config import (
    GEMINI_API_KEY,
    LLM_MODEL,
    TOP_K
)

from .document_loader import load_document
from .chunker import create_chunks
from .vectorstore import (
    add_documents,
    search_documents
)


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def add_file_to_rag(file_path):
    """
    Load, chunk and store a document.
    """

    documents = load_document(file_path)

    if not documents:
        return 0

    chunks = create_chunks(documents)

    if not chunks:
        return 0

    return add_documents(chunks)


def retrieve_documents(query):
    """
    Retrieve relevant document chunks.
    """

    return search_documents(
        query,
        top_k=TOP_K
    )


def generate_answer(
    query,
    retrieved_documents
):
    """
    Generate answer using retrieved document context.
    """

    if not retrieved_documents:

        return (
            "I could not find relevant information "
            "in the uploaded documents."
        )

    context_parts = []

    for index, document in enumerate(
        retrieved_documents,
        start=1
    ):

        source = document.get(
            "source",
            "Unknown"
        )

        page = document.get(
            "page",
            ""
        )

        text = document.get(
            "text",
            ""
        )

        context_parts.append(
            f"""
SOURCE {index}
File: {source}
Page: {page}

{text}
"""
        )

    context = "\n".join(context_parts)

    prompt = f"""
You are an AI assistant for students.

Answer the user's question using ONLY the
information contained in the provided document context.

If the answer is not available in the documents,
say that the information was not found in the
uploaded documents.

Do not invent facts.

User question:
{query}

Document context:
{context}

Instructions:
- Give a clear answer.
- Keep the answer easy for a student to understand.
- Mention the source file when useful.
- If the question asks for a summary, summarize the
  retrieved content.
"""

    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt
    )

    return response.text

