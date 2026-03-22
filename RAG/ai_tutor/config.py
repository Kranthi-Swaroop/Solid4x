import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

PROJECT_ROOT = Path(__file__).parent.parent
JEE_DIR = PROJECT_ROOT.parent / "JEE"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"
BM25_PATH = PROJECT_ROOT / "bm25_index.pkl"
CHUNKS_CACHE = PROJECT_ROOT / "chunks_cache.json"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemma-3-27b-it")
EMBEDDING_MODEL = "all-mpnet-base-v2"
EMBEDDING_DIMENSIONS = 768

CHUNK_SIZE = 2000
CHUNK_OVERLAP = 400
COLLECTION_NAME = "jee_docs"

SUBJECTS = {"Physics": "Physics", "Chemistry": "Chemistry", "Maths": "Mathematics"}
CLASS_LEVELS = ["11", "12"]
