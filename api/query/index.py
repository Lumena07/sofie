from fastapi import FastAPI, Request, HTTPException
import json
import os
from fastapi.middleware.cors import CORSMiddleware
from src.knowledge_base import KnowledgeBase

app = FastAPI()

# Initialize knowledge base
knowledge_base = KnowledgeBase()

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
        # Parse request
        body = await request.json()
        query = body.get("query")
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")

        # Query knowledge base
        result = knowledge_base.query_knowledge_base(query)
            
        return {
            "status": "success",
            "query": query,
            "response": result['answer'],
            "confidence": result['confidence']
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 