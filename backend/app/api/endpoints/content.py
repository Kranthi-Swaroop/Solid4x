import re
import os
import asyncio
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai
import edge_tts
from app.core.config import settings
from pathlib import Path

router = APIRouter()
client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Instantiate once (v1.x API requires instance, not class methods)
ytt_api = YouTubeTranscriptApi()

AUDIO_DIR = Path("data/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

class VideoProcessRequest(BaseModel):
    url: str
    target_language: str = "hi"

class VideoProcessResponse(BaseModel):
    video_id: str
    notes_markdown: str
    translated_summary: str
    audio_url: str

def extract_video_id(url: str) -> str:
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
        r"embed\/([0-9A-Za-z_-]{11})",
        r"shorts\/([0-9A-Za-z_-]{11})",
        r"live\/([0-9A-Za-z_-]{11})"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("Invalid YouTube URL")

async def generate_audio(text: str, file_path: str, voice: str = "hi-IN-SwaraNeural"):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(file_path)

# Broad language list to cover Hindi, English, and regional languages
LANGUAGE_PRIORITY = ['hi', 'en', 'hi-Latn', 'te', 'ta', 'bn', 'mr', 'gu', 'kn', 'ml', 'pa', 'ur']

@router.post("/process-video", response_model=VideoProcessResponse)
async def process_video(req: VideoProcessRequest):
    try:
        video_id = extract_video_id(req.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 1. Get Transcript using v1.x instance API
    transcript_text = ""
    try:
        # Strategy 1: Direct fetch with broad language list
        snippet = ytt_api.fetch(video_id, languages=LANGUAGE_PRIORITY)
        transcript_text = " ".join([entry.text for entry in snippet])
    except Exception:
        try:
            # Strategy 2: List available transcripts, pick the first one
            available = ytt_api.list(video_id)
            first_transcript = next(iter(available))
            snippet = ytt_api.fetch(video_id, languages=[first_transcript.language_code])
            transcript_text = " ".join([entry.text for entry in snippet])
        except Exception as e:
            err_msg = str(e).encode('ascii', 'ignore').decode('ascii')
            raise HTTPException(status_code=400, detail=f"Could not retrieve transcript: {err_msg}")

    if not transcript_text.strip():
        raise HTTPException(status_code=400, detail="Transcript was empty.")

    # Clip to stay within free-tier token limits (~15k tokens, ~10k chars safe)
    truncated_transcript = transcript_text[:10000]

    # 2. Generate Notes & Translation via Gemini (with retry for rate limits)
    prompt = f"""You are an elite JEE tutor. Analyze the following YouTube lecture transcript (which may be in English, Hindi, or a mix) and generate exactly TWO sections.
    Section 1 (English Notes): Detailed structured markdown notes in ENGLISH, capturing key concepts, headings, and formulas (using LaTeX notation).
    Section 2 (Translation): Translate ONLY a very clear 3-4 sentence summary of the core concepts into the `{req.target_language}` language.

    FORMAT:
    ---NOTES---
    [Markdown Notes Here]
    ---TRANSLATION---
    [Indic Translation Here]

    Transcript:
    {truncated_transcript}
    """

    notes = ""
    translation = ""
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt
            )
            res_text = response.text
            
            parts = res_text.split("---TRANSLATION---")
            notes = parts[0].replace("---NOTES---", "").strip()
            translation = parts[1].strip() if len(parts) > 1 else ""
            break  # Success, exit retry loop
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg and attempt < max_retries - 1:
                # Rate limited — wait and retry
                await asyncio.sleep(35)
                continue
            raise HTTPException(status_code=500, detail=f"Failed to generate AI notes: {err_msg}")

    # 3. Generate Indic Audio Dubbing
    audio_filename = f"{video_id}_{req.target_language}.mp3"
    audio_path = AUDIO_DIR / audio_filename
    audio_url = f"/static/audio/{audio_filename}"

    voice_map = {
        "hi": "hi-IN-SwaraNeural",
        "te": "te-IN-ShrutiNeural",
        "ta": "ta-IN-PallaviNeural",
        "bn": "bn-IN-TanishaaNeural"
    }
    voice = voice_map.get(req.target_language.lower(), "hi-IN-SwaraNeural")

    if translation and not audio_path.exists():
        await generate_audio(translation, str(audio_path), voice)

    return VideoProcessResponse(
        video_id=video_id,
        notes_markdown=notes,
        translated_summary=translation,
        audio_url=audio_url
    )
