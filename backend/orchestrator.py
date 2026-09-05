import os
from typing import Dict, Any, List, Optional
from typing_extensions import TypedDict
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from fastapi import HTTPException
from pydantic import BaseModel

# ==========================================
# Pydantic Schemas for Structured Output
# (Duplicated from main.py so LangChain can hook into it)
# ==========================================
class SentenceSentiment(BaseModel):
    sentence: str
    speaker: Optional[str] = None
    sentiment: str
    confidence: float
    explanation: Optional[str] = None

class AnalysisResponse(BaseModel):
    overall_sentiment: str = "neutral"
    confidence: float = 0.0
    conversation_summary: str = "Summary not generated."
    sentences: List[SentenceSentiment] = []
    emotions: List[str] = []
    action_items: List[str] = []
    kpis: Dict[str, Any] = {}

# ==========================================
# LangGraph State Definition
# ==========================================
class GraphState(TypedDict):
    text: str
    result: Optional[AnalysisResponse]
    error: Optional[str]

# ==========================================
# Nodes
# ==========================================
def analyze_sentiment(state: GraphState) -> GraphState:
    """LangGraph node: Analyzes sentiment using LangChain and Groq."""
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        return {"text": state["text"], "result": None, "error": "GROQ_API_KEY is missing in .env"}

    # Load system prompt
    try:
        prompt_path = os.path.join(os.path.dirname(__file__), '..', 'n8n', 'SYSTEM_PROMPT.md')
        with open(prompt_path, "r") as f:
            system_prompt = f.read()
    except Exception:
        system_prompt = "You are an AI analyst. Extract data according to the schema."

    try:
        # Initialize LangChain Groq Chat Model
        llm = ChatGroq(
            model="openai/gpt-oss-120b", 
            temperature=0.1,
            api_key=groq_api_key
        )
        
        # Force the LLM to output our Pydantic schema using .with_structured_output()
        structured_llm = llm.with_structured_output(AnalysisResponse)

        # Create the LangChain Prompt (Bypassing template parsing for the system message)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=state["text"])
        ]

        # Invoke the LLM directly with structured output
        print("Invoking LangChain/Groq pipeline...")
        response = structured_llm.invoke(messages)
        
        return {"text": state["text"], "result": response, "error": None}

    except Exception as e:
        print(f"LangChain Error: {str(e)}")
        return {"text": state["text"], "result": None, "error": str(e)}

# ==========================================
# Build LangGraph
# ==========================================
workflow = StateGraph(GraphState)
workflow.add_node("analyze", analyze_sentiment)
workflow.add_edge(START, "analyze")
workflow.add_edge("analyze", END)

# Compile the graph
app = workflow.compile()

# ==========================================
# Interface Function
# ==========================================
def call_orchestrator(text: str) -> Dict[str, Any]:
    """
    Executes the LangGraph state machine and returns the resulting JSON dict.
    """
    initial_state = {"text": text, "result": None, "error": None}
    
    # Run the graph
    final_state = app.invoke(initial_state)
    
    if final_state["error"]:
        raise HTTPException(status_code=502, detail=f"AI orchestration failed: {final_state['error']}")
        
    if not final_state["result"]:
        raise HTTPException(status_code=502, detail="AI returned empty result.")
        
    # Return the Pydantic object as a dictionary so main.py can process it
    return final_state["result"].dict()
