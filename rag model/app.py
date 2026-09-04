import os

import streamlit as st

from backend.document_manager import process_uploaded_file
from backend.query_engine import retrieve_documents
from backend.rag import generate_answer
from backend.vectorstore import get_document_count


# -------------------------------------------------
# Page configuration
# -------------------------------------------------

st.set_page_config(
    page_title="Student Notes AI",
    page_icon="📚",
    layout="wide"
)


# -------------------------------------------------
# Custom CSS
# -------------------------------------------------

st.markdown(
    """
    <style>
    .main-title {
        font-size: 36px;
        font-weight: 700;
    }

    .subtitle {
        font-size: 17px;
        color: #666;
        margin-bottom: 25px;
    }

    .source-box {
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -------------------------------------------------
# Header
# -------------------------------------------------

st.markdown(
    '<div class="main-title">📚 Student Notes AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Upload notes and ask questions using AI'
    '</div>',
    unsafe_allow_html=True
)


# -------------------------------------------------
# Session state
# -------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# -------------------------------------------------
# Sidebar - Upload Documents
# -------------------------------------------------

with st.sidebar:

    st.header("📤 Upload Documents")

    st.write(
        "Add study materials to the RAG system."
    )

    uploaded_files = st.file_uploader(
        "Choose documents",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )

    if st.button(
        "🚀 Add Documents to RAG",
        use_container_width=True
    ):

        if not uploaded_files:

            st.warning(
                "Please select at least one document."
            )

        else:

            for uploaded_file in uploaded_files:

                try:

                    with st.spinner(
                        f"Processing {uploaded_file.name}..."
                    ):

                        result = process_uploaded_file(
                            uploaded_file
                        )

                    st.success(
                        f"✓ {result['filename']}"
                    )

                    st.caption(
                        f"Pages/sections: "
                        f"{result['documents']}"
                    )

                    st.caption(
                        f"Chunks: "
                        f"{result['chunks']}"
                    )

                except Exception as error:

                    st.error(
                        f"Error processing "
                        f"{uploaded_file.name}: "
                        f"{error}"
                    )

    st.divider()

    st.subheader("📊 RAG Status")

    try:
        chunk_count = get_document_count()
    except Exception:
        chunk_count = 0

    st.metric(
        "Indexed Chunks",
        chunk_count
    )

    st.divider()

    st.caption(
        "Supported: PDF, DOCX, TXT"
    )


# -------------------------------------------------
# Function to display related documents
# -------------------------------------------------

def display_related_documents(
    documents,
    download_prefix="download"
):

    if not documents:

        st.info(
            "No related documents were found."
        )

        return

    st.markdown(
        "### 📄 Related Documents"
    )

    shown_sources = set()

    for index, document in enumerate(documents):

        source = document.get(
            "source",
            "Unknown"
        )

        page = document.get(
            "page",
            "N/A"
        )

        text = document.get(
            "text",
            ""
        )

        source_key = (
            source,
            page
        )

        if source_key in shown_sources:
            continue

        shown_sources.add(
            source_key
        )

        with st.expander(
            f"📄 {source} — Page {page}"
        ):

            st.write(text)

            file_path = os.path.join(
                "data",
                "uploads",
                source
            )

            if os.path.exists(file_path):

                try:

                    with open(
                        file_path,
                        "rb"
                    ) as file:

                        file_data = file.read()

                    st.download_button(
                        label="⬇️ Download Original Document",
                        data=file_data,
                        file_name=source,
                        key=(
                            f"{download_prefix}_"
                            f"{index}_"
                            f"{source}_"
                            f"{page}"
                        )
                    )

                except Exception as error:

                    st.warning(
                        f"Could not prepare download: "
                        f"{error}"
                    )


# -------------------------------------------------
# Chat history
# -------------------------------------------------

for message_index, message in enumerate(
    st.session_state.messages
):

    role = message["role"]

    with st.chat_message(role):

        st.markdown(
            message["content"]
        )

        if role == "assistant":

            documents = message.get(
                "documents",
                []
            )

            queries = message.get(
                "queries",
                []
            )

            display_related_documents(
                documents,
                download_prefix=f"history_{message_index}"
            )

            # Retrieval details

            with st.expander(
                "🔎 Retrieval details"
            ):

                if queries:

                    st.write(
                        "**Search queries used:**"
                    )

                    for query in queries:

                        st.write(
                            f"- {query}"
                        )

                else:

                    st.write(
                        "No query expansion information."
                    )


# -------------------------------------------------
# Chat input
# -------------------------------------------------

question = st.chat_input(
    "Ask a question about your uploaded notes..."
)


# -------------------------------------------------
# Process question
# -------------------------------------------------

if question:

    # ---------------------------------------------
    # Save user message
    # ---------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)


    # ---------------------------------------------
    # Generate AI response
    # ---------------------------------------------

    with st.chat_message("assistant"):

        try:

            # Retrieve documents

            with st.spinner(
                "🔎 Searching your notes..."
            ):

                documents, queries = retrieve_documents(
                    question
                )


            # Generate answer

            with st.spinner(
                "🤖 Generating answer..."
            ):

                answer = generate_answer(
                    question,
                    documents
                )


            # Display answer

            st.markdown(answer)


            # Display related documents

            display_related_documents(
                documents,
                download_prefix=(
                    f"chat_{len(st.session_state.messages)}"
                )
            )


            # Retrieval information

            with st.expander(
                "🔎 Retrieval details"
            ):

                if queries:

                    st.write(
                        "**Search queries used:**"
                    )

                    for query in queries:

                        st.write(
                            f"- {query}"
                        )


            # -------------------------------------
            # Save assistant response
            # -------------------------------------

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "documents": documents,
                    "queries": queries
                }
            )


        except Exception as error:

            error_message = (
                f"Something went wrong: {error}"
            )

            st.error(
                error_message
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                    "documents": [],
                    "queries": []
                }
            )