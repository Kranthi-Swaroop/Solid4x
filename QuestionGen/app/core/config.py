from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Solid4x QuestionGen API"
    API_V1_STR: str = "/api/v1"
    
    # CORS setup
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # MongoDB Settings
    MONGODB_URI: str = "mongodb://root:dbVAazDM1bCFRqVRikzLvbPkcfgGCo0WR2vl97NJZnZG5KMk9tAVvodhBqBsGn7l@168.119.148.180:27017/?directConnection=true"
    MONGODB_DB_NAME: str = "solid4x_db"

    # ChromaDB Settings
    CHROMA_URL: str = "https://chromadb.tashanwin.buzz"
    
    # Neo4j Settings (For Learner Knowledge Graph)
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
