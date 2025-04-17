from fastapi import FastAPI, Request, HTTPException
import json
import os
import requests
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
    return {"message": "API is running"}

@app.post("/api/query")
async def query(request: Request):
    try:
        # Get API key
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        # Parse request
        body = await request.json()
        query = body.get("query")
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")

        # Prepare OpenAI request
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
        
        # Make request to OpenAI
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        # Handle OpenAI response
        if response.status_code != 200:
            error_msg = f"OpenAI API error: Status {response.status_code}"
            try:
                error_json = response.json()
                if 'error' in error_json:
                    error_msg += f" - {error_json['error'].get('message', '')}"
            except:
                error_msg += f" - {response.text}"
            raise HTTPException(status_code=500, detail=error_msg)
            
        response_json = response.json()
        if "choices" not in response_json or not response_json["choices"]:
            raise HTTPException(status_code=500, detail="OpenAI API returned no response choices")
            
        return {
            "status": "success",
            "query": query,
            "response": response_json["choices"][0]["message"]["content"]
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 