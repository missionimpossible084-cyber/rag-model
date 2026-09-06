import os
import tempfile
from pathlib import Path

import streamlit as st


# ==================================================
# BACKEND IMPORTS
# ==================================================

from backend.config import (
    GEMINI_API_KEY,
    LLM_MODEL,
    UPLOAD_DIR
)

from backend.rag import (
    add_file_to_rag,
    retrieve_documents,
    generate_answer
)

from backend.vectorstore import (
    get_document_count
)

from backend.placement import (
    process_placement_message
)


# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Student AI Assistant",
    page_icon="🤖",
    layout="centered"
)


# ==================================================
# CSS
# ==================================================

st.markdown(
    """
    <style>

    /* ------------------------------------------
       Remove Streamlit sidebar
       ------------------------------------------ */

    [data-testid="stSidebar"] {
        display: none;
    }


    /* ------------------------------------------
       Main application width
       ------------------------------------------ */

    .block-container {
        max-width: 50vw;
        min-width: 420px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }


    /* ------------------------------------------
       Mobile
       ------------------------------------------ */

    @media (max-width: 900px) {

        .block-container {
            max-width: 92vw;
            min-width: 0;
        }

    }


    /* ------------------------------------------
       Header
       ------------------------------------------ */

    .app-title {
        text-align: center;
        font-size: 30px;
        font-weight: 700;
        margin-bottom: 5px;
    }


    .app-subtitle {
        text-align: center;
        color: #777;
        font-size: 14px;
        margin-bottom: 25px;
    }


    /* ------------------------------------------
       Chat messages
       ------------------------------------------ */

    [data-testid="stChatMessage"] {
        border-radius: 15px;
        padding: 8px;
    }


    /* ------------------------------------------
       Plus button
       ------------------------------------------ */

    .plus-btn button {
        border-radius: 50% !important;
        font-size: 22px !important;
        width: 45px !important;
        height: 45px !important;
        padding: 0 !important;
    }


    /* ------------------------------------------
       Upload box
       ------------------------------------------ */

    .upload-box {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }


    /* ------------------------------------------
       Menu buttons
       ------------------------------------------ */

    .menu-button button {
        border-radius: 10px !important;
    }


    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# SESSION STATE
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


if "show_menu" not in st.session_state:
    st.session_state.show_menu = False


if "placement_data" not in st.session_state:
    st.session_state.placement_data = {}


if "upload_mode" not in st.session_state:
    st.session_state.upload_mode = None


# ==================================================
# HEADER
# ==================================================

st.markdown(
    '<div class="app-title">Student AI Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="app-subtitle">'
    'Ask about your documents or placement prediction'
    '</div>',
    unsafe_allow_html=True
)


# ==================================================
# CHAT INPUT + PLUS BUTTON
# ==================================================

input_col1, input_col2 = st.columns(
    [1, 9],
    gap="small"
)


# --------------------------------------------------
# PLUS BUTTON
# --------------------------------------------------

with input_col1:

    st.markdown(
        '<div class="plus-btn">',
        unsafe_allow_html=True
    )

    plus_clicked = st.button(
        "＋",
        key="chat_plus_button",
        help="Add document"
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


if plus_clicked:

    st.session_state.show_menu = (
        not st.session_state.show_menu
    )

    st.rerun()


# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

with input_col2:

    user_prompt = st.chat_input(
        "Message Student AI Assistant..."
    )


# ==================================================
# PLUS MENU
# ==================================================

if st.session_state.show_menu:

    st.markdown(
        "### Add to Assistant"
    )


    menu_col1, menu_col2 = st.columns(
        2,
        gap="small"
    )


    # --------------------------------------------------
    # DOCUMENT FOR CHAT
    # --------------------------------------------------

    with menu_col1:

        st.markdown(
            '<div class="menu-button">',
            unsafe_allow_html=True
        )

        chat_option_clicked = st.button(
            "📄 Document for chat",
            key="chat_document_option",
            use_container_width=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


    # --------------------------------------------------
    # KNOWLEDGE BASE
    # --------------------------------------------------

    with menu_col2:

        st.markdown(
            '<div class="menu-button">',
            unsafe_allow_html=True
        )

        knowledge_option_clicked = st.button(
            "📚 Knowledge base",
            key="knowledge_document_option",
            use_container_width=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


    # --------------------------------------------------
    # SET UPLOAD MODE
    # --------------------------------------------------

    if chat_option_clicked:

        st.session_state.upload_mode = "chat"

        st.rerun()


    if knowledge_option_clicked:

        st.session_state.upload_mode = "knowledge"

        st.rerun()


    # ==================================================
    # FILE UPLOADER
    # ==================================================

    if st.session_state.upload_mode is not None:

        if st.session_state.upload_mode == "chat":

            st.info(
                "Upload a document to use only in this chat."
            )

        elif st.session_state.upload_mode == "knowledge":

            st.info(
                "Upload a document to add it to the "
                "permanent knowledge base."
            )


        uploaded_file = st.file_uploader(
            "Upload PDF, DOCX or TXT",
            type=[
                "pdf",
                "docx",
                "txt"
            ],
            key="document_uploader"
        )


        # ==================================================
        # PROCESS DOCUMENT
        # ==================================================

        if uploaded_file is not None:

            if st.button(
                "Add Document",
                key="add_document_button",
                use_container_width=True
            ):

                try:

                    # ------------------------------------------
                    # Get extension
                    # ------------------------------------------

                    suffix = Path(
                        uploaded_file.name
                    ).suffix


                    # ------------------------------------------
                    # Temporary file
                    # ------------------------------------------

                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=suffix
                    ) as temp_file:

                        temp_file.write(
                            uploaded_file.getvalue()
                        )

                        temp_path = temp_file.name


                    # ==================================================
                    # KNOWLEDGE BASE
                    # ==================================================

                    if (
                        st.session_state.upload_mode
                        == "knowledge"
                    ):

                        destination = (
                            UPLOAD_DIR /
                            uploaded_file.name
                        )


                        # Save document
                        with open(
                            destination,
                            "wb"
                        ) as file:

                            file.write(
                                uploaded_file.getvalue()
                            )


                        # Add to ChromaDB
                        with st.spinner(
                            "Processing document..."
                        ):

                            count = add_file_to_rag(
                                str(destination)
                            )


                        if count > 0:

                            st.success(
                                f"✅ {uploaded_file.name} "
                                f"added to the knowledge base "
                                f"({count} chunks)."
                            )

                        else:

                            st.warning(
                                "The document was uploaded, "
                                "but no text chunks were created."
                            )


                    # ==================================================
                    # CURRENT CHAT DOCUMENT
                    # ==================================================

                    else:

                        st.session_state[
                            "current_chat_document"
                        ] = {

                            "name":
                                uploaded_file.name,

                            "path":
                                temp_path
                        }


                        st.success(
                            f"✅ {uploaded_file.name} "
                            "is ready for this chat."
                        )


                except Exception as error:

                    st.error(
                        "Could not process document:\n\n"
                        f"{error}"
                    )


# ==================================================
# KNOWLEDGE BASE STATUS
# ==================================================

try:

    document_count = get_document_count()

except Exception:

    document_count = 0


# ==================================================
# DISPLAY CHAT HISTORY
# ==================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ==================================================
# INTENT DETECTION
# ==================================================

def is_placement_question(text):

    text = text.lower()

    placement_keywords = [

        "placement",

        "placed",

        "job prediction",

        "placement prediction",

        "placement chance",

        "placement probability",

        "will i get placed",

        "will i be placed",

        "predict my placement"

    ]

    return any(
        keyword in text
        for keyword in placement_keywords
    )


# ==================================================
# CURRENT CHAT DOCUMENT HANDLING
# ==================================================

def answer_from_current_chat_document(
    query
):

    document_info = st.session_state.get(
        "current_chat_document"
    )


    if not document_info:

        return None


    try:

        from backend.document_loader import (
            load_document
        )

        from backend.chunker import (
            create_chunks
        )

        from backend.embeddings import (
            embed_text
        )


        # ------------------------------------------
        # Load document
        # ------------------------------------------

        documents = load_document(
            document_info["path"]
        )


        # ------------------------------------------
        # Create chunks
        # ------------------------------------------

        chunks = create_chunks(
            documents
        )


        if not chunks:

            return None


        # ------------------------------------------
        # Query embedding
        # ------------------------------------------

        query_embedding = embed_text(
            query
        )


        # ------------------------------------------
        # Cosine similarity
        # ------------------------------------------

        import numpy as np

        scored_chunks = []


        for chunk in chunks:

            chunk_embedding = embed_text(
                chunk["text"]
            )


            query_vector = np.array(
                query_embedding
            )


            chunk_vector = np.array(
                chunk_embedding
            )


            denominator = (

                np.linalg.norm(
                    query_vector
                )

                *

                np.linalg.norm(
                    chunk_vector
                )

            )


            if denominator == 0:

                score = 0

            else:

                score = (

                    np.dot(
                        query_vector,
                        chunk_vector
                    )

                    /

                    denominator

                )


            scored_chunks.append(
                (
                    score,
                    chunk
                )
            )


        # ------------------------------------------
        # Sort chunks
        # ------------------------------------------

        scored_chunks.sort(
            key=lambda x: x[0],
            reverse=True
        )


        selected_chunks = [

            item[1]

            for item in scored_chunks[:5]

        ]


        # ------------------------------------------
        # Generate answer
        # ------------------------------------------

        return generate_answer(
            query,
            selected_chunks
        )


    except Exception as error:

        return (
            "I could not read the document "
            f"for this chat: {error}"
        )


# ==================================================
# GENERAL GEMINI ANSWER
# ==================================================

def general_gemini_answer(
    query
):

    from google import genai


    client = genai.Client(
        api_key=GEMINI_API_KEY
    )


    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=query
    )


    return response.text


# ==================================================
# PROCESS MESSAGE
# ==================================================

if user_prompt:

    # ==================================================
    # ADD USER MESSAGE
    # ==================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_prompt
        }
    )


    with st.chat_message("user"):

        st.markdown(
            user_prompt
        )


    # ==================================================
    # ASSISTANT RESPONSE
    # ==================================================

    with st.chat_message("assistant"):

        with st.spinner(
            "Thinking..."
        ):

            try:

                # ==========================================
                # PLACEMENT
                # ==========================================

                if is_placement_question(
                    user_prompt
                ):

                    result = (
                        process_placement_message(
                            user_prompt
                        )
                    )


                    # ------------------------------------------
                    # Missing placement information
                    # ------------------------------------------

                    if result["status"] == "missing":

                        missing = result[
                            "missing"
                        ]


                        friendly_names = {

                            "age":
                                "Age",

                            "gender":
                                "Gender",

                            "cgpa":
                                "CGPA",

                            "branch":
                                "Branch",

                            "internships_count":
                                "Number of internships",

                            "projects_count":
                                "Number of projects",

                            "certifications_count":
                                "Number of certifications"

                        }


                        missing_names = [

                            friendly_names.get(
                                item,
                                item
                            )

                            for item in missing

                        ]


                        answer = (

                            "I need a few more details "
                            "before I can make the placement "
                            "prediction.\n\n"

                            "**Please provide:**\n"

                            +

                            "\n".join(

                                f"- {item}"

                                for item in missing_names

                            )

                        )


                    # ------------------------------------------
                    # Placement prediction
                    # ------------------------------------------

                    else:

                        prediction = (
                            result["prediction"]
                        )


                        data = result[
                            "data"
                        ]


                        # Store latest data

                        st.session_state[
                            "placement_data"
                        ] = data


                        answer = (

                            "### Placement Prediction\n\n"

                            f"**Result:** "
                            f"{prediction['result']}\n\n"

                        )


                        if (
                            prediction[
                                "probability"
                            ] is not None
                        ):

                            answer += (

                                f"**Model probability:** "
                                f"{prediction['probability']:.2f}%\n\n"

                            )


                        answer += (

                            "**Information used:**\n"

                            f"- Age: {data['age']}\n"

                            f"- Gender: {data['gender']}\n"

                            f"- CGPA: {data['cgpa']}\n"

                            f"- Branch: {data['branch']}\n"

                            f"- Internships: "
                            f"{data['internships_count']}\n"

                            f"- Projects: "
                            f"{data['projects_count']}\n"

                            f"- Certifications: "
                            f"{data['certifications_count']}"

                        )


                # ==========================================
                # CURRENT CHAT DOCUMENT
                # ==========================================

                elif st.session_state.get(
                    "current_chat_document"
                ):

                    answer = (
                        answer_from_current_chat_document(
                            user_prompt
                        )
                    )


                # ==========================================
                # RAG KNOWLEDGE BASE
                # ==========================================

                else:

                    retrieved_documents = (
                        retrieve_documents(
                            user_prompt
                        )
                    )


                    if retrieved_documents:

                        answer = generate_answer(
                            user_prompt,
                            retrieved_documents
                        )

                    else:

                        answer = general_gemini_answer(
                            user_prompt
                        )


            except Exception as error:

                answer = (

                    "Something went wrong:\n\n"

                    f"`{error}`"

                )


        # ------------------------------------------
        # Display answer
        # ------------------------------------------

        st.markdown(
            answer
        )


    # ==================================================
    # SAVE ASSISTANT RESPONSE
    # ==================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
