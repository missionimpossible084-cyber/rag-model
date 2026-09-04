import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. "
        "Add it to the .env file."
    )

# Gemini models
LLM_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "gemini-embedding-001"

# Folders
UPLOAD_DIR = "data/uploads"
CHROMA_PATH = "chroma_db"

# Chroma collection
COLLECTION_NAME = "student_notes"

# Retrieval
TOP_K = 5
MULTI_QUERY_COUNT = 3