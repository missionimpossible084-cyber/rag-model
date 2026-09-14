from pathlib import Path
import os

from dotenv import load_dotenv


# ==================================================
# PROJECT ROOT
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ==================================================
# LOAD .ENV
# ==================================================

ENV_FILE = BASE_DIR / ".env"

load_dotenv(
    dotenv_path=ENV_FILE,
    override=True
)


# ==================================================
# GEMINI API KEY
# ==================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not GEMINI_API_KEY:
    raise RuntimeError(
        f"""
GEMINI_API_KEY was not found.

Expected .env file:
{ENV_FILE}

Make sure the file contains:

GEMINI_API_KEY=your_actual_gemini_api_key
"""
    )


# ==================================================
# GEMINI MODELS
# ==================================================

LLM_MODEL = "gemini-2.5-flash"

EMBEDDING_MODEL = "gemini-embedding-001"


# ==================================================
# DIRECTORIES
# ==================================================

DATA_DIR = BASE_DIR / "data"

UPLOAD_DIR = DATA_DIR / "uploads"

CHROMA_DIR = BASE_DIR / "chroma_db"

MODEL_DIR = BASE_DIR / "models"


# ==================================================
# CREATE DIRECTORIES
# ==================================================

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)

CHROMA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==================================================
# RAG SETTINGS
# ==================================================

COLLECTION_NAME = "student_documents"

TOP_K = 5

