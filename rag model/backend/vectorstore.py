import chromadb

from backend.config import (
    CHROMA_PATH,
    COLLECTION_NAME
)

from backend.embeddings import create_embedding


client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


def add_chunks(chunks):

    if not chunks:
        return 0

    ids = []
    documents = []
    metadatas = []
    embeddings = []

    for chunk in chunks:

        source = chunk["source"]

        # Convert Windows path into filename
        filename = source.replace("\\", "/").split("/")[-1]

        page = chunk["page"]

        page_value = (
            str(page)
            if page is not None
            else "N/A"
        )

        chunk_id = chunk["chunk_id"]

        unique_id = (
            f"{filename}"
            f"__page_{page_value}"
            f"__chunk_{chunk_id}"
        )

        # Avoid duplicate IDs
        ids.append(unique_id)

        documents.append(
            chunk["text"]
        )

        metadatas.append({
            "source": filename,
            "page": page_value,
            "chunk_id": str(chunk_id)
        })

        embeddings.append(
            create_embedding(
                chunk["text"]
            )
        )

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    return len(chunks)


def search_documents(
    query,
    top_k=5
):

    query_embedding = create_embedding(
        query
    )

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=top_k
    )

    documents = []

    if not results.get("documents"):
        return documents

    result_documents = results["documents"][0]

    result_metadatas = results["metadatas"][0]

    result_distances = (
        results.get("distances", [[]])[0]
    )

    for index, text in enumerate(
        result_documents
    ):

        metadata = result_metadatas[index]

        distance = None

        if index < len(result_distances):
            distance = result_distances[index]

        documents.append({

            "text": text,

            "source": metadata.get(
                "source",
                "Unknown"
            ),

            "page": metadata.get(
                "page",
                "N/A"
            ),

            "chunk_id": metadata.get(
                "chunk_id",
                ""
            ),

            "distance": distance

        })

    return documents


def get_document_count():

    return collection.count()