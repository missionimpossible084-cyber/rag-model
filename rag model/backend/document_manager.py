import os
import re

from backend.config import UPLOAD_DIR

from backend.document_loader import (
    load_document
)

from backend.chunker import (
    chunk_documents
)

from backend.vectorstore import (
    add_chunks
)


os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


def safe_filename(filename):

    filename = os.path.basename(
        filename
    )

    filename = re.sub(
        r"[^a-zA-Z0-9._-]",
        "_",
        filename
    )

    return filename


def process_uploaded_file(
    uploaded_file
):

    filename = safe_filename(
        uploaded_file.name
    )

    file_path = os.path.join(
        UPLOAD_DIR,
        filename
    )

    # Save original document
    with open(
        file_path,
        "wb"
    ) as file:

        file.write(
            uploaded_file.getbuffer()
        )

    # Extract text
    documents = load_document(
        file_path
    )

    if not documents:

        return {
            "filename": filename,
            "documents": 0,
            "chunks": 0
        }

    # Chunk
    chunks = chunk_documents(
        documents
    )

    # Generate embeddings + store
    stored_chunks = add_chunks(
        chunks
    )

    return {
        "filename": filename,
        "documents": len(documents),
        "chunks": stored_chunks
    }