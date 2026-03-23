import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Mount the RAG module
rag_path = str(Path(__file__).parent.parent.parent.parent.parent / "RAG")
if rag_path not in sys.path:
    sys.path.insert(0, rag_path)

from ai_tutor.generator import generate_answer

router = APIRouter()

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    num_chunks: int

@router.post("")
@router.post("/")
async def ai_tutor_chat(req: ChatRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        # generate_answer does actual LLM inference, run in thread if blocking
        result = generate_answer(req.query)
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            num_chunks=result["num_chunks_used"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
