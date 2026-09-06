import chromadb

from .config import (
    CHROMA_DIR,
    COLLECTION_NAME
)

from .embeddings import embed_documents


client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)


collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


def add_documents(chunks):
    """
    Add document chunks to ChromaDB.
    """

    if not chunks:
        return 0

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = embed_documents(texts)

    ids = []
    metadatas = []

    for index, chunk in enumerate(chunks):

        source = chunk["source"]
        page = chunk["page"]
        chunk_id = chunk["chunk_id"]

        document_id = (
            f"{source}_{page}_{chunk_id}_{index}"
        )

        ids.append(document_id)

        metadatas.append(
            {
                "source": source,
                "page": str(page) if page else "",
                "chunk_id": str(chunk_id),
            }
        )

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(chunks)


def search_documents(query, top_k=5):
    """
    Search ChromaDB using query embedding.
    """

    from .embeddings import embed_text

    query_embedding = embed_text(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = []

    if not results.get("documents"):
        return documents

    result_documents = results["documents"][0]
    result_metadatas = results["metadatas"][0]

    for text, metadata in zip(
        result_documents,
        result_metadatas
    ):

        documents.append(
            {
                "text": text,
                "source": metadata.get(
                    "source",
                    "Unknown"
                ),
                "page": metadata.get(
                    "page",
                    ""
                ),
            }
        )

    return documents


def get_document_count():
    """
    Return number of stored chunks.
    """

    return collection.count()

