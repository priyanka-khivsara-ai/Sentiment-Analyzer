from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from orchestrator import call_orchestrator, AnalysisResponse
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

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
    Accepts a .txt conversation file, validates it, and triggers the LangGraph AI workflow.
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
    if len(text) > 100000:
        raise HTTPException(status_code=400, detail="File is too large. Maximum size is 100,000 characters.")

    # 5. Execute LangGraph Orchestrator
    # The LangGraph workflow automatically constructs the prompt, invokes ChatGroq, 
    # uses with_structured_output for strict Pydantic parsing, and returns the result.
    return call_orchestrator(text)
