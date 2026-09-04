import os
import requests
from fastapi import HTTPException
from typing import Dict, Any

def call_n8n_webhook(text: str) -> Dict[str, Any]:
    """
    Sends the parsed conversation text to the n8n orchestration workflow.
    Expects n8n to return a JSON payload matching our AnalysisResponse Pydantic schema.
    """
    webhook_url = os.getenv("N8N_WEBHOOK_URL")
    
    if not webhook_url:
        # Developer logs / fail-fast if environment is not set up correctly
        print("ERROR: N8N_WEBHOOK_URL environment variable is missing.")
        raise HTTPException(
            status_code=500, 
            detail="Server configuration error. AI orchestration URL is missing."
        )
        
    try:
        # Send the text as a JSON payload to n8n
        response = requests.post(
            webhook_url,
            json={"conversation_text": text},
            timeout=45  # 45 seconds timeout. LLMs can be slow, but we shouldn't hang forever
        )
        
        # Raise an exception if the HTTP request returned an error status code
        response.raise_for_status()
        
        # Return the parsed JSON from n8n. 
        # (This will be validated against our Pydantic model back in main.py)
        return response.json()
        
    except requests.exceptions.Timeout:
        # Handle API Timeout explicitly as requested in error handling requirements
        print("ERROR: n8n webhook timed out after 45 seconds.")
        raise HTTPException(
            status_code=504, 
            detail="AI Analysis timed out. The orchestration workflow took too long."
        )
    except requests.exceptions.RequestException as e:
        # Handle n8n unavailability or network failures
        print(f"ERROR: Failed to communicate with n8n: {str(e)}")
        raise HTTPException(
            status_code=502, 
            detail="Failed to communicate with the AI orchestration layer (n8n unavailable)."
        )
    except ValueError:
        # Handle malformed JSON response from n8n
        print("ERROR: n8n did not return valid JSON.")
        raise HTTPException(
            status_code=502,
            detail="Received an invalid or malformed response from the AI orchestration layer."
        )
