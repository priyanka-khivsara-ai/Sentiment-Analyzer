from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from n8n_client import call_n8n_webhook
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
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
    overall_sentiment: str = "neutral"
    confidence: float = 0.0
    conversation_summary: str = "Summary not generated."
    sentences: List[SentenceSentiment] = []
    emotions: List[str] = []
    action_items: List[str] = []  # Extra Creativity Feature
    kpis: Dict[str, Any] = {}

# ==========================================
# App Initialization
# ==========================================
app = FastAPI(
    title="Sentiment Analyzer API",
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

    # 5. Send to n8n AI Orchestration Layer
    # The n8n client handles timeouts, network errors, and parses the JSON.
    n8n_response = call_n8n_webhook(text)
    
    # 6. Validate AI Response
    # By passing the raw dict into our Pydantic model, FastAPI automatically 
    # validates that the LLM returned exactly the schema we requested.
    try:
        validated_data = AnalysisResponse(**n8n_response)
        return validated_data
    except Exception as e:
        print(f"ERROR: AI Response validation failed. {str(e)}")
        raise HTTPException(
            status_code=502, 
            detail="The AI analysis returned an unexpected format. Please try again."
        )
