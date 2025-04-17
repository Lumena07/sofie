from fastapi import FastAPI, Request, HTTPException
import json
import os
import requests
from typing import Optional

app = FastAPI()

async def process_query(query: str) -> Optional[str]:
    """Process a query using OpenAI."""
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("Error: OPENAI_API_KEY environment variable not set")
            return None

        headers = {
            "Authorization": f"Bearer {api_key}",
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
            json=data,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"OpenAI API error: Status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
        response_json = response.json()
        if "choices" not in response_json or not response_json["choices"]:
            print("OpenAI API error: No choices in response")
            print(f"Response: {response_json}")
            return None
            
        return response_json["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        print("OpenAI API timeout")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

@app.post("/api/query")
async def handle_query(request: Request):
    try:
        body = await request.json()
        query = body.get("query")
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")

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
        print(f"Request error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 