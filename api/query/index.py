from fastapi import FastAPI, Request, HTTPException
import json
import os
import requests
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Query API is running"}

async def process_query(query: str) -> Optional[str]:
    """Process a query using OpenAI."""
    print("Starting process_query")  # Debug log
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        print(f"API key present: {bool(api_key)}")  # Debug log
        if not api_key:
            print("Error: OPENAI_API_KEY environment variable not set")
            return None

        print("Preparing request to OpenAI")  # Debug log
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
        
        print("Sending request to OpenAI")  # Debug log
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        print(f"OpenAI response status: {response.status_code}")  # Debug log
        
        if response.status_code != 200:
            print(f"OpenAI API error: Status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
        response_json = response.json()
        if "choices" not in response_json or not response_json["choices"]:
            print("OpenAI API error: No choices in response")
            print(f"Response: {response_json}")
            return None
            
        print("Successfully got response from OpenAI")  # Debug log
        return response_json["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error in process_query: {str(e)}")  # Debug log
        return None

@app.post("/api/query")
async def handle_query(request: Request):
    print("Received request to /api/query")  # Debug log
    try:
        body = await request.json()
        print(f"Parsed request body: {body}")  # Debug log
        
        query = body.get("query")
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")

        print("Calling process_query")  # Debug log
        response_text = await process_query(query)
        if not response_text:
            print("No response from process_query")  # Debug log
            raise HTTPException(status_code=500, detail="Failed to process query")

        print("Successfully processed query")  # Debug log
        return {
            "status": "success",
            "query": query,
            "response": response_text
        }
    except json.JSONDecodeError:
        print("Invalid JSON in request")  # Debug log
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        print(f"Error in handle_query: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e)) 