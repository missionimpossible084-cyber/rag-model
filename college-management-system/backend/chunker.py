"""
Text chunking utilities for the RAG system.

No LangChain is required.
Compatible with Python 3.14.
"""


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 150
):
    """
    Split a single text into overlapping chunks.
    """

    if not text:
        return []

    text = text.strip()

    if not text:
        return []

    # Prevent invalid configuration
    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        # Stop when we reached the end
        if end >= text_length:
            break

        # Move forward while keeping overlap
        start = end - chunk_overlap

    return chunks


def create_chunks(documents):
    """
    Convert loaded documents into RAG chunks.

    Expected input:

    [
        {
            "text": "...",
            "source": "notes.pdf",
            "page": 1
        }
    ]

    Returns:

    [
        {
            "text": "...",
            "source": "notes.pdf",
            "page": 1,
            "chunk_id": 0
        }
    ]
    """

    chunks = []

    for document in documents:

        text = document.get(
            "text",
            ""
        )

        source = document.get(
            "source",
            "Unknown"
        )

        page = document.get(
            "page",
            None
        )

        text_chunks = chunk_text(
            text=text,
            chunk_size=1000,
            chunk_overlap=150
        )

        for chunk_id, chunk in enumerate(
            text_chunks
        ):

            chunks.append(
                {
                    "text": chunk,
                    "source": source,
                    "page": page,
                    "chunk_id": chunk_id
                }
            )

    return chunks

