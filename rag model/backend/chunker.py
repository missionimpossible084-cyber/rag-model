from langchain_text_splitters import RecursiveCharacterTextSplitter


splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ]
)


def chunk_documents(documents):

    chunks = []

    for document in documents:

        text = document["text"]

        split_texts = splitter.split_text(text)

        for chunk_number, chunk_text in enumerate(
            split_texts
        ):

            chunks.append({
                "text": chunk_text,
                "source": document["source"],
                "page": document["page"],
                "chunk_id": chunk_number
            })

    return chunks