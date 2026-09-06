from pathlib import Path
import os

from dotenv import load_dotenv


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env
load_dotenv(BASE_DIR / ".env")


# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Add it to the .env file."
    )


# Gemini models
LLM_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "gemini-embedding-001"


# Directories
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
CHROMA_DIR = BASE_DIR / "chroma_db"
MODEL_DIR = BASE_DIR / "models"


# Create required directories
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)


# RAG
COLLECTION_NAME = "student_documents"
TOP_K = 5

