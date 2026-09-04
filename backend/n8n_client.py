import os
import requests
import json
from fastapi import HTTPException
from typing import Dict, Any

def call_n8n_webhook(text: str) -> Dict[str, Any]:
    """
    Acts as the orchestration layer. Attempts to use n8n if configured,
    otherwise uses the local Groq API key to orchestrate the LLM directly.
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    # If we have the Groq key, we will orchestrate the LLM call directly in Python!
    if groq_api_key:
        print("Orchestrating live AI analysis via Groq...")
        
        # 1. Load our engineered system prompt
        try:
            # We locate the SYSTEM_PROMPT.md file we created earlier
            prompt_path = os.path.join(os.path.dirname(__file__), '..', 'n8n', 'SYSTEM_PROMPT.md')
            with open(prompt_path, "r") as f:
                system_prompt = f.read()
        except Exception as e:
            print("Warning: Could not read SYSTEM_PROMPT.md, using hardcoded fallback.")
            system_prompt = "Analyze the text and return valid JSON with overall_sentiment, confidence, conversation_summary, sentences, emotions, action_items, kpis."
            
        # 2. Call the Groq API (OpenAI compatible)
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama3-8b-8192",  # Fast, free open-source model
                    "response_format": { "type": "json_object" }, # Force structured output
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ],
                    "temperature": 0.1 # Low temperature for analytical consistency
                },
                timeout=30
            )
            response.raise_for_status()
            
            # 3. Parse the LLM response
            llm_content = response.json()["choices"][0]["message"]["content"]
            return json.loads(llm_content)
            
        except Exception as e:
            print(f"Groq API Error: {str(e)}")
            raise HTTPException(status_code=502, detail="Failed to process conversation with live AI.")

    # --- Fallback to n8n Webhook logic below ---
    webhook_url = os.getenv("N8N_WEBHOOK_URL")
    
    if not webhook_url:
        raise HTTPException(
            status_code=500, 
            detail="Server configuration error. AI orchestration URL or API Key is missing."
        )
        
    try:
        # Send the text as a JSON payload to n8n
        response = requests.post(webhook_url, json={"conversation_text": text}, timeout=45)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="AI Analysis timed out.")
    except Exception as e:
        raise HTTPException(status_code=502, detail="Failed to communicate with n8n.")
