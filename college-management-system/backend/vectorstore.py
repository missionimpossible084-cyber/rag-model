import chromadb

from .config import CHROMA_DIR, COLLECTION_NAME, TOP_K
from .embeddings import embed_documents, embed_text


# -----------------------------------------
# Create ChromaDB client
# -----------------------------------------

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)


# -----------------------------------------
# Create / load collection
# -----------------------------------------

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


# -----------------------------------------
# Add documents
# -----------------------------------------

def add_documents(chunks):

    if not chunks:
        return 0

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    # Generate embeddings
    embeddings = embed_documents(texts)

    ids = []
    metadatas = []

    for index, chunk in enumerate(chunks):

        source = chunk.get("source", "Unknown")
        page = chunk.get("page", "")
        chunk_id = chunk.get("chunk_id", index)

        document_id = (
            f"{source}_{page}_{chunk_id}_{index}"
        )

        ids.append(document_id)

        metadatas.append({
            "source": str(source),
            "page": str(page),
            "chunk_id": str(chunk_id)
        })

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(chunks)


# -----------------------------------------
# Search documents
# -----------------------------------------

def search_documents(query, top_k=None):

    if top_k is None:
        top_k = TOP_K

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

        documents.append({
            "text": text,
            "source": metadata.get(
                "source",
                "Unknown"
            ),
            "page": metadata.get(
                "page",
                ""
            )
        })

    return documents


# -----------------------------------------
# Get number of stored chunks
# -----------------------------------------

def get_document_count():

    return collection.count()

