import os
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# BACKEND IMPORTS — existing backend is kept unchanged
# ============================================================

from backend.config import GEMINI_API_KEY, LLM_MODEL, UPLOAD_DIR
from backend.rag import add_file_to_rag, retrieve_documents, generate_answer
from backend.vectorstore import get_document_count
from backend.placement import process_placement_message


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Student AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "messages": [],
    "show_plus_menu": False,
    "upload_mode": None,
    "current_chat_document": None,
    "placement_data": {},
    "chat_history": [],
    "events": [],
    "announcements": [],
    "pending_prompt": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value.copy() if isinstance(value, list) else (
            value.copy() if isinstance(value, dict) else value
        )


# ============================================================
# CSS — ChatGPT-style application
# ============================================================

st.markdown(
    """
<style>
:root {
    --sidebar-width: 260px;
    --composer-width: 820px;
}

/* ===== GLOBAL ===== */
.stApp,
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 75% 12%, rgba(91, 76, 255, .18), transparent 28%),
        radial-gradient(circle at 20% 85%, rgba(0, 200, 255, .10), transparent 30%),
        linear-gradient(135deg, #0b1020 0%, #111827 48%, #0b1324 100%) !important;
    color: #f7f9ff !important;
}

[data-testid="stAppViewContainer"] > .main {
    background: transparent !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

#MainMenu, footer {
    display: none !important;
}

.block-container {
    max-width: 980px !important;
    padding: 0 24px 125px !important;
    margin: 0 auto !important;
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1220 0%, #111a2c 52%, #0b1526 100%) !important;
    border-right: 1px solid rgba(126,145,190,.20) !important;
}

section[data-testid="stSidebar"] > div {
    padding: 12px 10px !important;
}

.sidebar-brand {
    color: #f7f9ff;
    font-size: 18px;
    font-weight: 700;
    padding: 7px 8px 16px;
}

.sidebar-section-title {
    color: #777b83;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .06em;
    padding: 18px 8px 7px;
}

/* ===== HEADER ===== */
.main-shell {
    width: 100%;
}

.topbar {
    height: 58px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid rgba(148,163,184,.16);
    margin-bottom: 8px;
}

.topbar-title {
    font-size: 17px;
    font-weight: 750;
    color: #f8fbff;
}

.topbar-status {
    color: #9eabc7;
    font-size: 12px;
}

/* ===== EMPTY HOME ===== */
.welcome {
    max-width: 720px;
    margin: 18vh auto 30px;
    text-align: center;
}

.welcome-logo {
    width: 58px;
    height: 58px;
    margin: 0 auto 16px;
    border-radius: 18px;
    background: linear-gradient(135deg, #6c63ff, #00b8d9);
    color: #fff;
    box-shadow: 0 12px 30px rgba(108,99,255,.22);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 23px;
}

.welcome h1 {
    margin: 0;
    color: #f8fbff;
    font-size: 30px;
    letter-spacing: -.7px;
}

.welcome p {
    margin-top: 8px;
    color: #aebbd5;
    font-size: 15px;
}

/* ===== CHAT MESSAGES ===== */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: 0 !important;
    padding: 10px 0 !important;
    margin: 0 !important;
}

[data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
    max-width: 86%;
    border-radius: 18px;
    padding: 13px 17px !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    margin-left: auto;
    background: linear-gradient(135deg, #6c63ff, #4f8cff) !important;
    color: #ffffff !important;
    box-shadow: 0 7px 20px rgba(79,140,255,.16);
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] p,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] li,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] span {
    color: #ffffff !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
    margin-right: auto;
    background: linear-gradient(135deg, rgba(30,41,59,.98), rgba(23,37,61,.98)) !important;
    border: 1px solid rgba(120,140,180,.22) !important;
    box-shadow: 0 8px 24px rgba(0,0,0,.18);
}

[data-testid="stChatMessageContent"] {
    color: #edf3ff !important;
    font-size: 15px !important;
    line-height: 1.65 !important;
}

[data-testid="stChatMessageContent"] p,
[data-testid="stChatMessageContent"] li,
[data-testid="stChatMessageContent"] span {
    color: #edf3ff !important;
}

.user-attachment {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 7px 11px;
    margin: 0 0 8px;
    border: 1px solid rgba(255,255,255,.35);
    border-radius: 10px;
    background: rgba(255,255,255,.18);
    color: #ffffff;
    font-size: 13px;
}

/* ===== COMPOSER =====
   Streamlit's horizontal block containing the message input is
   anchored to the viewport. The previous version shifted it by
   the sidebar width, which pushed the controls out of the box.
*/
div[data-testid="stHorizontalBlock"]:has(
    input[placeholder="Message Student AI..."]
) {
    position: fixed !important;
    z-index: 1000000 !important;
    left: 50% !important;
    bottom: 14px !important;
    transform: translateX(calc(-50% + 130px)) !important;

    width: min(
        var(--composer-width),
        calc(100vw - 310px)
    ) !important;
    max-width: var(--composer-width) !important;

    display: flex !important;
    align-items: center !important;
    gap: 8px !important;

    padding: 7px 9px !important;
    margin: 0 !important;

    background: linear-gradient(135deg, rgba(27,36,54,.98), rgba(20,30,49,.98)) !important;
    border: 1px solid rgba(126,145,190,.38) !important;
    border-radius: 24px !important;
    box-shadow: 0 16px 45px rgba(0,0,0,.38), 0 0 0 1px rgba(108,99,255,.06) inset !important;
}

/* Remove Streamlit column padding */
div[data-testid="stHorizontalBlock"]:has(
    input[placeholder="Message Student AI..."]
) > div {
    padding: 0 !important;
    margin: 0 !important;
}

/* Hide labels */
div[data-testid="stHorizontalBlock"]:has(
    input[placeholder="Message Student AI..."]
) label {
    display: none !important;
}

/* Input */
div[data-testid="stHorizontalBlock"]:has(
    input[placeholder="Message Student AI..."]
) [data-testid="stTextInput"] {
    margin: 0 !important;
}

div[data-testid="stHorizontalBlock"]:has(
    input[placeholder="Message Student AI..."]
) [data-testid="stTextInput"] > div {
    border: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
}

div[data-testid="stHorizontalBlock"]:has(
    input[placeholder="Message Student AI..."]
) input {
    height: 42px !important;
    min-height: 42px !important;
    padding: 0 6px !important;
    border: 0 !important;
    outline: 0 !important;
    box-shadow: none !important;
    background: transparent !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #8ea2ff !important;
    font-size: 15px !important;
    font-weight: 500 !important;
}

div[data-testid="stHorizontalBlock"]:has(
    input[placeholder="Message Student AI..."]
) input::placeholder {
    color: #9aa8c2 !important;
    -webkit-text-fill-color: #9aa8c2 !important;
    opacity: 1 !important;
}

/* Streamlit/BaseWeb can override the native input color. These selectors force
   the typed query to remain bright and readable on the dark composer. */
div[data-testid="stHorizontalBlock"]:has(input[placeholder="Message Student AI..."]) [data-baseweb="input"],
div[data-testid="stHorizontalBlock"]:has(input[placeholder="Message Student AI..."]) [data-baseweb="base-input"] {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
}

div[data-testid="stHorizontalBlock"]:has(input[placeholder="Message Student AI..."]) [data-baseweb="input"] input,
div[data-testid="stHorizontalBlock"]:has(input[placeholder="Message Student AI..."]) [data-baseweb="base-input"] input {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    background: transparent !important;
    opacity: 1 !important;
}

/* Plus + Send */
div[data-testid="stHorizontalBlock"]:has(
    input[placeholder="Message Student AI..."]
) button {
    width: 40px !important;
    min-width: 40px !important;
    height: 40px !important;
    min-height: 40px !important;
    padding: 0 !important;
    margin: 0 !important;
    border-radius: 50% !important;
    border: 1px solid #dce1ff !important;
    background: rgba(255,255,255,.07) !important;
    color: #dce5ff !important;
    font-size: 19px !important;
}

div[data-testid="stHorizontalBlock"]:has(
    input[placeholder="Message Student AI..."]
) button:hover {
    background: rgba(108,99,255,.20) !important;
}

/* Gradient send button */
div[data-testid="stHorizontalBlock"]:has(input[placeholder="Message Student AI..."]) button[kind="primary"] {
    background: linear-gradient(135deg, #6c63ff, #00a8e8) !important;
    color: #ffffff !important;
    border: 0 !important;
    box-shadow: 0 6px 15px rgba(108,99,255,.25);
}

/* ===== PLUS MENU / PANELS ===== */
.plus-menu,
.upload-panel,
.quick-actions {
    width: min(100%, 820px);
    margin-left: auto;
    margin-right: auto;
}

.plus-menu {
    padding: 10px;
    margin-top: 5px;
    border: 1px solid #e5e5e5;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(25,35,54,.98), rgba(20,30,49,.98));
    border-color: rgba(126,145,190,.25);
    box-shadow: 0 12px 30px rgba(79,91,160,.10);
}

.menu-label {
    color: #9eabc7;
    font-size: 12px;
    font-weight: 600;
    padding: 2px 6px 8px;
}

.upload-panel {
    padding: 14px;
    margin-top: 8px;
    border: 1px solid rgba(126,145,190,.25);
    border-radius: 14px;
    background: rgba(20,30,49,.96);
}

.upload-title {
    color: #f3f6ff;
    font-size: 15px;
    font-weight: 650;
}

.upload-description {
    color: #9eabc7;
    font-size: 13px;
    margin: 4px 0 10px;
}

.quick-actions {
    margin-top: 25px;
}

.quick-title {
    color: #5d68a1;
    font-size: 13px;
    margin-bottom: 9px;
}

/* ===== STREAMLIT BUTTON / INPUT COLORS ===== */
.stButton > button,
.stTextInput input,
.stTextArea textarea,
[data-testid="stFileUploader"] {
    color: #f5f7ff !important;
}

.stTextInput input,
.stTextArea textarea {
    background: rgba(15,23,42,.75) !important;
    border-color: rgba(126,145,190,.28) !important;
    -webkit-text-fill-color: #f5f7ff !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #94a3bd !important;
    -webkit-text-fill-color: #94a3bd !important;
}

/* ===== COLORFUL CONTROLS ===== */
.stButton > button {
    border: 1px solid #dfe3ff !important;
    background: linear-gradient(135deg, #1e2a44, #182238) !important;
    color: #e9eeff !important;
    border-radius: 12px !important;
    font-weight: 650 !important;
}

.stButton > button:hover {
    border-color: #aeb7ff !important;
    background: linear-gradient(135deg, #2b3a62, #21365a) !important;
    color: #ffffff !important;
}

[data-testid="stFileUploader"] {
    border: 1px dashed #aeb8ff !important;
    background: rgba(15,23,42,.72) !important;
    border-radius: 14px !important;
}

/* Keep the conversation area visually clear and leave room for the fixed composer. */
.chat-area {
    padding-bottom: 25px;
}


/* ===== VISIBLE QUERY EMPHASIS ===== */
.user-query-label {
    display: inline-block;
    margin-bottom: 7px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: rgba(255,255,255,.72);
}
.assistant-query-context {
    margin-top: 2px;
    margin-bottom: 10px;
    color: #93a5c7;
    font-size: 12px;
}

/* ===== MOBILE ===== */
@media (max-width: 800px) {
    .block-container {
        padding: 0 12px 120px !important;
    }

    div[data-testid="stHorizontalBlock"]:has(
        input[placeholder="Message Student AI..."]
    ) {
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: calc(100vw - 18px) !important;
        max-width: none !important;
        bottom: 8px !important;
    }

    .welcome {
        margin-top: 12vh;
    }

    .welcome h1 {
        font-size: 25px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def new_chat():
    """Start a clean conversation while preserving history."""
    if st.session_state.messages:
        first_user = next(
            (m["content"] for m in st.session_state.messages if m["role"] == "user"),
            "New conversation",
        )
        title = first_user.strip().replace("\n", " ")
        st.session_state.chat_history.insert(0, title[:60])

    st.session_state.messages = []
    st.session_state.current_chat_document = None
    st.session_state.upload_mode = None
    st.session_state.show_plus_menu = False
    st.session_state.pending_prompt = None


def is_placement_question(text):
    keywords = [
        "placement chance",
        "placement chances",
        "placement prediction",
        "will i get placed",
        "placement probability",
        "job placement",
    ]
    lower = text.lower()
    return any(k in lower for k in keywords)


def extract_document_text(file_path):
    """Extract text from PDF, DOCX or TXT for chat-only document Q&A."""
    suffix = Path(file_path).suffix.lower()

    if suffix == ".pdf":
        import fitz

        doc = fitz.open(file_path)
        return "\n\n".join(page.get_text() for page in doc)

    if suffix == ".docx":
        from docx import Document

        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    if suffix == ".txt":
        return Path(file_path).read_text(encoding="utf-8", errors="ignore")

    raise ValueError("Unsupported document type.")


def answer_from_current_chat_document(question):
    document = st.session_state.current_chat_document

    if not document:
        return "No document is attached to this conversation."

    text = document.get("text", "")
    if not text.strip():
        return "The uploaded document contains no readable text."

    # Keep the prompt within practical model limits.
    max_chars = 80000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[Document truncated for this query.]"

    try:
        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = f"""
You are a student document assistant.

Answer the student's question using the attached document as the primary source.
If the answer is not present in the document, say clearly that it is not found
in the document instead of inventing information.

DOCUMENT:
{text}

STUDENT QUESTION:
{question}
"""

        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt,
        )
        return response.text or "I could not generate an answer from the document."

    except Exception as error:
        return f"Could not answer from the uploaded document: `{error}`"


def general_gemini_answer(question):
    try:
        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=question,
        )
        return response.text or "I could not generate an answer."
    except Exception as error:
        return f"Something went wrong while contacting the AI model: `{error}`"


def save_uploaded_file(uploaded_file):
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getvalue())
        return temp_file.name


def process_user_message(user_prompt):
    """Route the question to placement, chat-document, RAG, or general AI."""
    if is_placement_question(user_prompt):
        result = process_placement_message(user_prompt)

        if result["status"] == "missing":
            friendly_names = {
                "age": "Age",
                "gender": "Gender",
                "cgpa": "CGPA",
                "branch": "Branch",
                "internships_count": "Number of internships",
                "projects_count": "Number of projects",
                "certifications_count": "Number of certifications",
            }

            missing_names = [
                friendly_names.get(item, item)
                for item in result["missing"]
            ]

            return (
                "### Placement Prediction\n\n"
                "I need a few more details before I can make the prediction.\n\n"
                "**Please provide:**\n"
                + "\n".join(f"- {item}" for item in missing_names)
            )

        prediction = result["prediction"]
        data = result["data"]
        st.session_state.placement_data = data

        answer = (
            "### Placement Prediction\n\n"
            f"**Result:** {prediction['result']}\n\n"
        )

        if prediction.get("probability") is not None:
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
        return answer

    if st.session_state.get("current_chat_document"):
        return answer_from_current_chat_document(user_prompt)

    retrieved_documents = retrieve_documents(user_prompt)

    if retrieved_documents:
        return generate_answer(user_prompt, retrieved_documents)

    return general_gemini_answer(user_prompt)


# ============================================================
# LEFT SIDEBAR — NEW CHAT + HISTORY
# ============================================================

with st.sidebar:
    st.markdown('<div class="sidebar-brand">🤖 Student AI</div>', unsafe_allow_html=True)

    if st.button("＋  New chat", key="new_chat", use_container_width=True):
        new_chat()
        st.rerun()

    st.markdown(
        '<div class="sidebar-section-title">History</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.chat_history:
        for index, title in enumerate(st.session_state.chat_history[:20]):
            if st.button(
                f"💬  {title}",
                key=f"history_{index}",
                use_container_width=True,
            ):
                st.info("This history entry is currently a title-only record. "
                        "Persistent conversation replay can be added with a database.")
    else:
        st.caption("No previous chats yet.")

    st.markdown(
        '<div class="sidebar-section-title">Knowledge base</div>',
        unsafe_allow_html=True,
    )

    try:
        document_count = get_document_count()
        st.caption(f"📚 {document_count} documents/chunks available")
    except Exception:
        st.caption("📚 Knowledge base")


# ============================================================
# MAIN AREA
# ============================================================

st.markdown('<div class="main-shell">', unsafe_allow_html=True)

st.markdown(
    """
<div class="topbar">
    <div class="topbar-title">Student AI Assistant</div>
    <div class="topbar-status">AI • RAG • Documents</div>
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# CHAT HISTORY DISPLAY
# ============================================================

if not st.session_state.messages:
    st.markdown(
        """
<div class="welcome">
    <div class="welcome-logo">✦</div>
    <h1>How can I help you today?</h1>
    <p>Ask questions, search your documents, or use your student knowledge base.</p>
</div>
""",
        unsafe_allow_html=True,
    )
else:
    st.markdown('<div class="chat-area">', unsafe_allow_html=True)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown('<div class="user-query-label">Your query</div>', unsafe_allow_html=True)
            if message.get("attachment"):
                st.markdown(
                    f'<div class="user-attachment">📄 '
                    f'{message["attachment"]}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown(message["content"])

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# PLUS MENU
# ============================================================

if st.session_state.show_plus_menu:
    st.markdown(
        """
<div class="plus-menu">
    <div class="menu-label">Add to this conversation</div>
</div>
""",
        unsafe_allow_html=True,
    )

    menu1, menu2, menu3, menu4 = st.columns(4)

    with menu1:
        if st.button("📎 Upload for chat", key="menu_chat", use_container_width=True):
            st.session_state.upload_mode = "chat"
            st.session_state.show_plus_menu = False
            st.rerun()

    with menu2:
        if st.button("📚 Document for RAG", key="menu_rag", use_container_width=True):
            st.session_state.upload_mode = "knowledge"
            st.session_state.show_plus_menu = False
            st.rerun()

    with menu3:
        if st.button("📅 Event", key="menu_event", use_container_width=True):
            st.session_state.upload_mode = "event"
            st.session_state.show_plus_menu = False
            st.rerun()

    with menu4:
        if st.button("📢 Announcement", key="menu_announcement", use_container_width=True):
            st.session_state.upload_mode = "announcement"
            st.session_state.show_plus_menu = False
            st.rerun()


# ============================================================
# UPLOAD / EVENT / ANNOUNCEMENT PANELS
# ============================================================

if st.session_state.upload_mode is not None:
    mode = st.session_state.upload_mode

    st.markdown('<div class="upload-panel">', unsafe_allow_html=True)

    if mode == "chat":
        st.markdown('<div class="upload-title">📎 Upload for this chat</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="upload-description">'
            'The document is available only to this conversation. '
            'Ask questions about it from the search bar.'
            '</div>',
            unsafe_allow_html=True,
        )

        uploaded_file = st.file_uploader(
            "Choose a document",
            type=["pdf", "docx", "txt"],
            key="chat_document_uploader",
        )

        if uploaded_file is not None:
            if st.button("Attach to chat", key="attach_chat", use_container_width=True):
                try:
                    temp_path = save_uploaded_file(uploaded_file)
                    text = extract_document_text(temp_path)

                    st.session_state.current_chat_document = {
                        "name": uploaded_file.name,
                        "path": temp_path,
                        "text": text,
                    }

                    st.session_state.messages.append(
                        {
                            "role": "user",
                            "content": f"I uploaded **{uploaded_file.name}**. "
                                       "You can ask me questions about this document.",
                            "attachment": uploaded_file.name,
                        }
                    )

                    st.session_state.upload_mode = None
                    st.success(f"{uploaded_file.name} is attached to this chat.")
                    st.rerun()

                except Exception as error:
                    st.error(f"Could not read the document: {error}")

    elif mode == "knowledge":
        st.markdown('<div class="upload-title">📚 Add document to RAG</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="upload-description">'
            'The document will be indexed into your existing RAG knowledge base. '
            'Future questions can retrieve information from it.'
            '</div>',
            unsafe_allow_html=True,
        )

        uploaded_file = st.file_uploader(
            "Choose a document",
            type=["pdf", "docx", "txt"],
            key="rag_document_uploader",
        )

        if uploaded_file is not None:
            if st.button("Add to knowledge base", key="add_rag", use_container_width=True):
                try:
                    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
                    destination = UPLOAD_DIR / uploaded_file.name
                    destination.write_bytes(uploaded_file.getvalue())

                    with st.spinner("Indexing document into RAG..."):
                        count = add_file_to_rag(str(destination))

                    if count > 0:
                        st.success(
                            f"✅ {uploaded_file.name} added to RAG "
                            f"({count} chunks)."
                        )
                        st.session_state.upload_mode = None
                    else:
                        st.warning(
                            "The document was uploaded, but no text chunks were created."
                        )

                except Exception as error:
                    st.error(f"Could not index the document: {error}")

    elif mode == "event":
        st.markdown('<div class="upload-title">📅 Add event</div>', unsafe_allow_html=True)

        event_name = st.text_input("Event name", placeholder="e.g. Semester exam")
        event_date = st.date_input("Date")
        event_note = st.text_input("Note", placeholder="Optional details")

        if st.button("Save event", key="save_event", use_container_width=True):
            if event_name.strip():
                st.session_state.events.append(
                    {
                        "name": event_name.strip(),
                        "date": str(event_date),
                        "note": event_note.strip(),
                    }
                )
                st.success("Event added.")
                st.session_state.upload_mode = None
                st.rerun()
            else:
                st.warning("Enter an event name.")

    elif mode == "announcement":
        st.markdown('<div class="upload-title">📢 Add announcement</div>', unsafe_allow_html=True)

        announcement_title = st.text_input(
            "Announcement title",
            placeholder="e.g. Internal assessment notice",
        )
        announcement_text = st.text_area(
            "Announcement",
            placeholder="Write the announcement...",
        )

        if st.button("Save announcement", key="save_announcement", use_container_width=True):
            if announcement_title.strip() and announcement_text.strip():
                st.session_state.announcements.append(
                    {
                        "title": announcement_title.strip(),
                        "text": announcement_text.strip(),
                    }
                )
                st.success("Announcement added.")
                st.session_state.upload_mode = None
                st.rerun()
            else:
                st.warning("Enter both a title and announcement.")

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# QUICK ACTIONS ON EMPTY CHAT
# ============================================================

if not st.session_state.messages:
    st.markdown('<div class="quick-actions">', unsafe_allow_html=True)
    st.markdown('<div class="quick-title">Try asking</div>', unsafe_allow_html=True)

    q1, q2, q3, q4 = st.columns(4)

    quick_prompts = [
        ("📄 Summarize a document", "Summarize my uploaded document"),
        ("🎓 Help with studies", "Help me understand an important study topic"),
        ("📊 Placement chances", "What are my placement chances?"),
        ("📚 Search knowledge", "Search my knowledge base"),
    ]

    for col, (label, prompt) in zip([q1, q2, q3, q4], quick_prompts):
        with col:
            if st.button(label, key=f"quick_{prompt}", use_container_width=True):
                user_prompt = prompt
                send_clicked = True

    st.markdown("</div>", unsafe_allow_html=True)




# ============================================================
# SEARCH BAR
# Plus is intentionally positioned on the LEFT of the input.
# ============================================================

st.markdown('<div class="search-row">', unsafe_allow_html=True)

plus_col, input_col, send_col = st.columns([0.65, 10, 0.65], gap="small")

with plus_col:
    st.markdown('<div class="plus-button">', unsafe_allow_html=True)
    plus_clicked = st.button(
        "＋",
        key="plus_button",
        help="Uploads, RAG documents, events and announcements",
    )
    st.markdown("</div>", unsafe_allow_html=True)

with input_col:
    user_prompt = st.text_input(
        "Search",
        placeholder="Message Student AI...",
        label_visibility="collapsed",
        key="main_chat_input",
    )

with send_col:
    st.markdown('<div class="send-button">', unsafe_allow_html=True)
    send_clicked = st.button(
        "➤",
        key="send_button",
        help="Send message",
        type="primary",
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

if plus_clicked:
    st.session_state.show_plus_menu = not st.session_state.show_plus_menu
    st.rerun()


# ============================================================
# MESSAGE SUBMISSION + AI PROCESSING
# ============================================================

# First step: capture the typed query and immediately rerun. This makes the
# user's question appear in the chat area before the AI starts working.
if send_clicked and user_prompt and user_prompt.strip():
    clean_prompt = user_prompt.strip()

    attachment_name = None
    if st.session_state.current_chat_document:
        attachment_name = st.session_state.current_chat_document.get("name")

    st.session_state.messages.append(
        {
            "role": "user",
            "content": clean_prompt,
            "attachment": attachment_name,
        }
    )
    st.session_state.pending_prompt = clean_prompt
    st.session_state.main_chat_input = ""
    st.rerun()

# Second step: the query is already visible above. Now generate the answer.
if st.session_state.pending_prompt:
    pending = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

    with st.spinner("Student AI is thinking..."):
        try:
            answer = process_user_message(pending)
        except Exception as error:
            answer = f"I couldn't process that request: `{error}`"

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )
    st.rerun()
