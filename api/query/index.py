from http.client import HTTPException
from fastapi import FastAPI, Request
import json

app = FastAPI()

@app.post("/api/query")
async def handle_query(request: Request):
    try:
        # Get the request body
        body = await request.json()
        
        # Extract the query from the request body
        query = body.get("query")
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")

        # Process the query (implement your logic here)
        # For now, just echo back the query
        response = {
            "status": "success",
            "query": query,
            "response": f"Processed query: {query}"
        }
        
        return response
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 