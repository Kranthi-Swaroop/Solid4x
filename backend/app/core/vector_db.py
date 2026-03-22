import chromadb
from chromadb.config import Settings
from app.core.config import settings as app_settings
import httpx

class VectorDB:
    client = None
    collection = None

vector_db = VectorDB()

def connect_to_chroma():
    # Attempting HTTP connection based on the URL provided
    # Standard chromadb HttpClient setup
    host = app_settings.CHROMA_URL
    vector_db.client = chromadb.HttpClient(
        host=host,
        settings=Settings(
            allow_reset=True,
            anonymized_telemetry=False
        )
    )
    # Ensure collection exists
    vector_db.collection = vector_db.client.get_or_create_collection(name="pyqs_collection")

def get_vector_db():
    return vector_db.collection
