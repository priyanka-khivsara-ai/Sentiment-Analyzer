from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# ==========================================
# Pydantic Schemas for Structured Output
# ==========================================
# These schemas ensure our API always returns a predictable, validated JSON structure
# to the React frontend, acting as a strict contract.

class SentenceSentiment(BaseModel):
    sentence: str
    speaker: Optional[str] = None
    sentiment: str  # Expected: 'positive', 'negative', 'neutral'
    confidence: float
    explanation: Optional[str] = None

class AnalysisResponse(BaseModel):
    overall_sentiment: str
    confidence: float
    conversation_summary: str
    sentences: List[SentenceSentiment]
    emotions: List[str]
    kpis: Dict[str, Any]

# ==========================================
# App Initialization
# ==========================================
app = FastAPI(
    title="CallSense AI API",
    description="Backend API for intelligent conversation analysis",
    version="1.0.0"
)

# Configure CORS to allow our React frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted to the Vercel/Netlify URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Endpoints
# ==========================================
@app.get("/health")
async def health_check():
    """Simple health check endpoint to verify the API is running."""
    return {"status": "healthy"}

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_conversation(file: UploadFile = File(...)):
    """
    Accepts a .txt conversation file, validates it, and will eventually forward 
    it to n8n/LLM for processing.
    """
    # 1. File type validation (Security: Do not execute uploaded content)
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .txt files are allowed.")
    
    # 2. Read file content
    content = await file.read()
    text = content.decode("utf-8").strip()
    
    # 3. Empty file validation
    if not text:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    
    # 4. Oversized file validation (Preventing massive payload processing)
    if len(text) > 100000:  # ~100k characters is a safe limit for a coding round
        raise HTTPException(status_code=400, detail="File is too large. Maximum size is 100,000 characters.")

    # TODO: In the next steps, we will implement the actual n8n orchestration call here.
    # For now, we return a mock structured response to prove the architecture flow.
    return AnalysisResponse(
        overall_sentiment="neutral",
        confidence=0.0,
        conversation_summary="Analysis pending integration.",
        sentences=[],
        emotions=[],
        kpis={}
    )
