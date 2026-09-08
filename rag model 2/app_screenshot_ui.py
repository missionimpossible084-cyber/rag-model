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
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Student AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================================================
# SCREENSHOT-STYLE UI
# ==================================================

st.markdown("""
<style>

/* ---------- GLOBAL ---------- */

header[data-testid="stHeader"] {
    background: transparent;
}

.stApp {
    background: #0d1521;
    color: #f5f7fb;
}

.block-container {
    max-width: 100%;
    padding: 0 3.2rem 7rem 3.2rem;
}

#MainMenu, footer {
    visibility: hidden;
}

/* ---------- HOME WRAPPER ---------- */

.ai-page {
    max-width: 1220px;
    margin: 0 auto;
}

/* ---------- HERO ---------- */

.hero {
    text-align: center;
    padding-top: 62px;
}

.ai-logo {
    width: 58px;
    height: 58px;
    margin: 0 auto 18px auto;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #172233;
    border: 1px solid #344154;
    font-size: 31px;
}

.greeting {
    font-size: 31px;
    font-weight: 700;
    letter-spacing: -0.5px;
}

.subtitle {
    margin-top: 10px;
    color: #aebbd0;
    font-size: 18px;
}

/* ---------- CHAT INPUT ---------- */

/* Streamlit's native chat input is used so the existing backend
   remains unchanged. The CSS makes it resemble the screenshot. */

[data-testid="stChatInput"] {
    max-width: 820px;
    margin: 42px auto 0 auto;
}

[data-testid="stChatInput"] > div {
    background: #1b2534 !important;
    border: 1px solid #344154 !important;
    border-radius: 20px !important;
    min-height: 112px;
    box-shadow: 0 10px 35px rgba(0,0,0,.20);
}

[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #f5f7fb !important;
    font-size: 17px !important;
    padding: 17px 18px !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #aebbd0 !important;
}

/* ---------- QUICK ACTIONS ---------- */

.quick-actions {
    max-width: 820px;
    margin: 24px auto 0 auto;
}

.quick-actions-title {
    display: none;
}

div[data-testid="stHorizontalBlock"] {
    gap: 12px;
}

/* Quick action buttons */
.quick-action-row button {
    background: #141e2c !important;
    color: #d9e1ed !important;
    border: 1px solid #2e3b4f !important;
    border-radius: 24px !important;
    min-height: 44px !important;
    font-size: 14px !important;
    white-space: nowrap !important;
}

.quick-action-row button:hover {
    border-color: #536dfe !important;
    color: white !important;
}

/* ---------- ASSISTANT SECTION ---------- */

.assistant-section {
    max-width: 1220px;
    margin: 130px auto 0 auto;
    border-top: 1px solid #293547;
    padding-top: 25px;
}

.assistant-heading {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 22px;
}

.assistant-plus {
    width: 64px;
    height: 64px;
    min-width: 64px;
    border-radius: 50%;
    background: #536dfe;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40px;
    box-shadow: 0 8px 24px rgba(83,109,254,.25);
}

.assistant-title {
    font-size: 21px;
    font-weight: 700;
}

.assistant-description {
    color: #aebbd0;
    font-size: 15px;
    margin-top: 5px;
}

/* ---------- FEATURE CARDS ---------- */

.feature-card {
    background: #141e2c;
    border: 1px solid #2d394c;
    border-radius: 15px;
    min-height: 215px;
    padding: 20px;
    box-sizing: border-box;
}

.feature-icon {
    width: 49px;
    height: 49px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    background: #536dfe;
}

.feature-title {
    margin-top: 15px;
    font-size: 18px;
    font-weight: 700;
}

.feature-text {
    color: #aebbd0;
    font-size: 14px;
    line-height: 1.45;
    margin-top: 8px;
    min-height: 43px;
}

.feature-button button {
    margin-top: 13px;
    width: 100%;
    border-radius: 10px !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    min-height: 38px !important;
}

.event-button button {
    background: #536dfe !important;
}

.announcement-button button {
    background: #20b982 !important;
}

.research-button button {
    background: #8050df !important;
}

.document-button button {
    background: #f57c20 !important;
}

/* ---------- CHAT AREA ---------- */

.chat-area {
    max-width: 900px;
    margin: 30px auto 0 auto;
}

[data-testid="stChatMessage"] {
    background: #141e2c;
    border: 1px solid #29374b;
    border-radius: 16px;
    padding: 12px 18px;
    margin-bottom: 12px;
}

[data-testid="stChatMessage"] p {
    color: #edf2f8;
}

/* ---------- UPLOAD PANEL ---------- */

.upload-panel {
    max-width: 820px;
    margin: 25px auto;
    background: #141e2c;
    border: 1px solid #2d394c;
    border-radius: 16px;
    padding: 20px;
}

.upload-title {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 8px;
}

.upload-description {
    color: #aebbd0;
    margin-bottom: 15px;
}

/* ---------- RESPONSIVE ---------- */

@media (max-width: 900px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .hero {
        padding-top: 30px;
    }

    .greeting {
        font-size: 25px;
    }

    .assistant-section {
        margin-top: 80px;
    }

}

</style>
""", unsafe_allow_html=True)


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
# HOME / HERO
# ==================================================

show_home = len(st.session_state.messages) == 0

st.markdown('<div class="ai-page">', unsafe_allow_html=True)

if show_home:
    st.markdown("""
    <div class="hero">
        <div class="ai-logo">🤖</div>
        <div class="greeting">Hello, Naveen Kumar</div>
        <div class="subtitle">How can I help you today?</div>
    </div>
    """, unsafe_allow_html=True)


# ==================================================
# CHAT HISTORY
# ==================================================

if not show_home:
    st.markdown('<div class="chat-area">', unsafe_allow_html=True)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    st.markdown('</div>', unsafe_allow_html=True)


# ==================================================
# CHAT INPUT
# ==================================================

user_prompt = st.chat_input("Ask anything...")


# ==================================================
# QUICK ACTIONS
# ==================================================

if show_home:
    st.markdown('<div class="quick-actions">', unsafe_allow_html=True)

    qa1, qa2, qa3, qa4 = st.columns(4)

    with qa1:
        st.markdown('<div class="quick-action-row">', unsafe_allow_html=True)
        summarize_clicked = st.button(
            "📄  Summarize a document",
            key="quick_summary",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with qa2:
        st.markdown('<div class="quick-action-row">', unsafe_allow_html=True)
        placement_clicked = st.button(
            "📊  Check placement chances",
            key="quick_placement",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with qa3:
        st.markdown('<div class="quick-action-row">', unsafe_allow_html=True)
        explain_clicked = st.button(
            "💡  Explain a concept",
            key="quick_explain",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with qa4:
        st.markdown('<div class="quick-action-row">', unsafe_allow_html=True)
        study_clicked = st.button(
            "🎓  Help with my studies",
            key="quick_studies",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Quick buttons create a normal chat prompt.
    if summarize_clicked:
        st.session_state.messages.append({
            "role": "user",
            "content": "Summarize a document"
        })
        st.rerun()

    if placement_clicked:
        st.session_state.messages.append({
            "role": "user",
            "content": "Check my placement chances"
        })
        st.rerun()

    if explain_clicked:
        st.session_state.messages.append({
            "role": "user",
            "content": "Explain a concept"
        })
        st.rerun()

    if study_clicked:
        st.session_state.messages.append({
            "role": "user",
            "content": "Help me with my studies"
        })
        st.rerun()


# ==================================================
# ADD TO YOUR ASSISTANT
# ==================================================

if show_home:

    st.markdown("""
    <div class="assistant-section">

        <div class="assistant-heading">

            <div class="assistant-plus">+</div>

            <div>
                <div class="assistant-title">
                    Add to Your Assistant
                </div>

                <div class="assistant-description">
                    Keep track of important things and get better,
                    personalized help.
                </div>
            </div>

        </div>

    </div>
    """, unsafe_allow_html=True)

    card1, card2, card3, card4 = st.columns(4)

    with card1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📅</div>
            <div class="feature-title">Events</div>
            <div class="feature-text">
                Add important dates, deadlines, exams and events.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="feature-button event-button">', unsafe_allow_html=True)
        event_clicked = st.button(
            "＋ Add Event",
            key="add_event",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with card2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📢</div>
            <div class="feature-title">Announcements</div>
            <div class="feature-text">
                Stay updated with the latest notices and updates.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="feature-button announcement-button">', unsafe_allow_html=True)
        announcement_clicked = st.button(
            "＋ Add Announcement",
            key="add_announcement",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with card3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <div class="feature-title">Research Papers</div>
            <div class="feature-text">
                Save and manage your research papers.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="feature-button research-button">', unsafe_allow_html=True)
        research_clicked = st.button(
            "＋ Add Research Paper",
            key="add_research",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with card4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📁</div>
            <div class="feature-title">Documents</div>
            <div class="feature-text">
                Upload and organize your important documents.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="feature-button document-button">', unsafe_allow_html=True)
        document_clicked = st.button(
            "＋ Add Document",
            key="add_document",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    if event_clicked:
        st.info("Event management can be connected here.")

    if announcement_clicked:
        st.info("Announcement management can be connected here.")

    if research_clicked:
        st.session_state.show_menu = True
        st.session_state.upload_mode = "knowledge"
        st.rerun()

    if document_clicked:
        st.session_state.show_menu = True
        st.session_state.upload_mode = "knowledge"
        st.rerun()


# ==================================================
# PLUS / UPLOAD MENU
# ==================================================

# The original plus-button functionality is preserved through
# a compact upload section below the cards.
if show_home or st.session_state.upload_mode is not None:

    st.markdown('<div class="upload-panel">', unsafe_allow_html=True)

    if st.session_state.upload_mode is None:
        st.markdown(
            '<div class="upload-title">＋ Add a document</div>'
            '<div class="upload-description">'
            'Use the uploader when you want to add a document to this assistant.'
            '</div>',
            unsafe_allow_html=True
        )

        upload_col1, upload_col2 = st.columns(2)

        with upload_col1:
            chat_option_clicked = st.button(
                "📄 Document for this chat",
                key="home_chat_document",
                use_container_width=True
            )

        with upload_col2:
            knowledge_option_clicked = st.button(
                "📚 Add to knowledge base",
                key="home_knowledge_document",
                use_container_width=True
            )

        if chat_option_clicked:
            st.session_state.upload_mode = "chat"
            st.rerun()

        if knowledge_option_clicked:
            st.session_state.upload_mode = "knowledge"
            st.rerun()

    else:

        if st.session_state.upload_mode == "chat":
            st.markdown(
                '<div class="upload-title">📄 Document for this chat</div>'
                '<div class="upload-description">'
                'This document will be used only for the current conversation.'
                '</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="upload-title">📚 Knowledge base</div>'
                '<div class="upload-description">'
                'This document will be added to your permanent RAG knowledge base.'
                '</div>',
                unsafe_allow_html=True
            )

        uploaded_file = st.file_uploader(
            "Upload PDF, DOCX or TXT",
            type=["pdf", "docx", "txt"],
            key="document_uploader"
        )

        if uploaded_file is not None:

            if st.button(
                "Add Document",
                key="add_document_button",
                use_container_width=True
            ):

                try:

                    suffix = Path(uploaded_file.name).suffix

                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=suffix
                    ) as temp_file:

                        temp_file.write(uploaded_file.getvalue())
                        temp_path = temp_file.name

                    if st.session_state.upload_mode == "knowledge":

                        destination = UPLOAD_DIR / uploaded_file.name

                        with open(destination, "wb") as file:
                            file.write(uploaded_file.getvalue())

                        with st.spinner("Processing document..."):
                            count = add_file_to_rag(str(destination))

                        if count > 0:
                            st.success(
                                f"✅ {uploaded_file.name} added to the knowledge "
                                f"base ({count} chunks)."
                            )
                        else:
                            st.warning(
                                "The document was uploaded, but no text chunks "
                                "were created."
                            )

                    else:

                        st.session_state["current_chat_document"] = {
                            "name": uploaded_file.name,
                            "path": temp_path
                        }

                        st.success(
                            f"✅ {uploaded_file.name} is ready for this chat."
                        )

                except Exception as error:
                    st.error(
                        "Could not process document:\n\n"
                        f"{error}"
                    )

st.markdown('</div>', unsafe_allow_html=True)


# ==================================================
# PROCESS USER MESSAGE
# ==================================================

if user_prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                # ==========================================
                # PLACEMENT
                # ==========================================

                if is_placement_question(user_prompt):

                    result = process_placement_message(user_prompt)

                    if result["status"] == "missing":

                        missing = result["missing"]

                        friendly_names = {
                            "age": "Age",
                            "gender": "Gender",
                            "cgpa": "CGPA",
                            "branch": "Branch",
                            "internships_count": "Number of internships",
                            "projects_count": "Number of projects",
                            "certifications_count": "Number of certifications"
                        }

                        missing_names = [
                            friendly_names.get(item, item)
                            for item in missing
                        ]

                        answer = (
                            "I need a few more details before I can make "
                            "the placement prediction.\n\n"
                            "**Please provide:**\n"
                            +
                            "\n".join(
                                f"- {item}"
                                for item in missing_names
                            )
                        )

                    else:

                        prediction = result["prediction"]
                        data = result["data"]

                        st.session_state["placement_data"] = data

                        answer = (
                            "### Placement Prediction\n\n"
                            f"**Result:** {prediction['result']}\n\n"
                        )

                        if prediction["probability"] is not None:

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
                            f"- Internships: {data['internships_count']}\n"
                            f"- Projects: {data['projects_count']}\n"
                            f"- Certifications: {data['certifications_count']}"
                        )

                # ==========================================
                # CURRENT CHAT DOCUMENT
                # ==========================================

                elif st.session_state.get("current_chat_document"):

                    answer = answer_from_current_chat_document(
                        user_prompt
                    )

                # ==========================================
                # RAG KNOWLEDGE BASE
                # ==========================================

                else:

                    retrieved_documents = retrieve_documents(
                        user_prompt
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

        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

st.markdown("</div>", unsafe_allow_html=True)
