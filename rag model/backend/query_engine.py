from google import genai

from backend.config import (
    GEMINI_API_KEY,
    LLM_MODEL,
    TOP_K,
    MULTI_QUERY_COUNT
)

from backend.vectorstore import (
    search_documents
)


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def generate_queries(question):

    prompt = f"""
You are a query expansion system for a
student educational document search engine.

Generate {MULTI_QUERY_COUNT} different search
queries for the student's question.

Each query should search for the same information
using different wording.

Rules:
- Keep the meaning of the original question.
- Use important technical terms.
- Do not answer the question.
- Return only one query per line.
- Do not number the queries.

Student question:

{question}
"""

    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt
    )

    lines = response.text.split("\n")

    queries = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Remove possible numbering
        if line[0:2] in [
            "1.",
            "2.",
            "3."
        ]:
            line = line[2:].strip()

        queries.append(line)

    queries = queries[
        :MULTI_QUERY_COUNT
    ]

    # Always retain original question
    if question not in queries:

        queries.insert(
            0,
            question
        )

    return queries


def retrieve_documents(question):

    queries = generate_queries(
        question
    )

    unique_documents = {}

    for query in queries:

        results = search_documents(
            query,
            top_k=TOP_K
        )

        for document in results:

            key = (
                document["source"],
                document["page"],
                document["chunk_id"]
            )

            if key not in unique_documents:

                unique_documents[key] = document

    documents = list(
        unique_documents.values()
    )

    return documents, queries