"""
RAG Chatbot — FastAPI server wrapping the ai_tutor pipeline.
Run:  cd RAG && python -m uvicorn server:app --reload --port 8000
"""
import sys
from pathlib import Path

# Ensure ai_tutor package is importable
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Solid4x AI Tutor")

# CORS — allow the Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    num_chunks: int


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        from ai_tutor.generator import generate_answer
        result = generate_answer(req.query)
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            num_chunks=result["num_chunks_used"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


import edge_tts
from fastapi.responses import StreamingResponse
import re

class TTSRequest(BaseModel):
    text: str

@app.post("/api/tts")
async def generate_tts(req: TTSRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    # Strip markdown and source citations so the voice doesn't read them
    clean_text = re.sub(r'\[Source \d+:.*?\]', '', req.text)
    clean_text = clean_text.replace("*", "").replace("#", "")
    
    # Create the edge-tts communicator with a premium Hindi voice
    communicate = edge_tts.Communicate(clean_text, "hi-IN-SwaraNeural")
    
    async def audio_stream():
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]
                
    return StreamingResponse(audio_stream(), media_type="audio/mpeg")

@app.get("/api/health")
def health():
    return {"status": "ok"}
