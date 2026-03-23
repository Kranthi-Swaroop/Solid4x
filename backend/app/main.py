from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.router import api_router
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.vector_db import connect_to_chroma
from app.core.neo4j_db import connect_to_neo4j, close_neo4j_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Execute exactly on server startup
    await connect_to_mongo()
    await connect_to_neo4j()
    connect_to_chroma()
    
    yield  # Server runs here
    
    # Execute on server teardown
    await close_neo4j_connection()
    await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles

app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount Audio Files so frontend can stream them freely
import os
os.makedirs("data/audio", exist_ok=True)
app.mount("/static/audio", StaticFiles(directory="data/audio"), name="audio")


@app.get("/")
def root():
    return {"message": "Welcome to Solid4x QuestionGen API"}
