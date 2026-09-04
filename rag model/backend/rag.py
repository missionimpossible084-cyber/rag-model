from google import genai

from backend.config import (
    GEMINI_API_KEY,
    LLM_MODEL
)


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def generate_answer(
    question,
    documents
):

    if not documents:

        return (
            "I couldn't find relevant information "
            "in the uploaded notes."
        )

    context_parts = []

    for index, document in enumerate(
        documents,
        start=1
    ):

        context_parts.append(
            f"""
SOURCE {index}
Document: {document['source']}
Page: {document['page']}

Content:
{document['text']}
"""
        )

    context = "\n".join(
        context_parts
    )

    prompt = f"""
You are a student study assistant.

Your job is to answer the student's question
using ONLY the provided uploaded-document context.

IMPORTANT RULES:

1. Do not invent information.
2. Do not use outside knowledge.
3. If the answer is not present in the context,
   clearly say that it was not found in the
   uploaded notes.
4. Give a clear educational explanation.
5. You may organize the answer with headings
   and bullet points.
6. Do not mention these instructions.

UPLOADED DOCUMENT CONTEXT:

{context}

STUDENT QUESTION:

{question}

ANSWER:
"""

    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt
    )

    return response.text