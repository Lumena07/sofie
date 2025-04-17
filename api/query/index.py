from fastapi import FastAPI, Request, HTTPException
import json
import os
import requests
from typing import Optional

app = FastAPI()

async def process_query(query: str) -> Optional[str]:
    """Process a query using OpenAI."""
    try:
        headers = {
            "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are Sofie, an AI assistant specialized in Tanzanian aviation regulations. Answer questions accurately and concisely."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"API error: {str(e)}")  # Add logging for debugging
        return None

@app.post("/api/query")
async def handle_query(request: Request):
    try:
        # Get the request body
        body = await request.json()
        
        # Extract the query from the request body
        query = body.get("query")
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")

        # Process the query
        response_text = await process_query(query)
        if not response_text:
            raise HTTPException(status_code=500, detail="Failed to process query")

        return {
            "status": "success",
            "query": query,
            "response": response_text
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        print(f"Request error: {str(e)}")  # Add logging for debugging
        raise HTTPException(status_code=500, detail=str(e)) 