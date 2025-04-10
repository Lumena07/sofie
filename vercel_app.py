from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.agent_orchestrator import AgentOrchestrator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()
agent_orchestrator = AgentOrchestrator()

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/query")
async def process_query(request: Request):
    try:
        data = await request.json()
        query = data.get("query")
        
        if not query:
            return JSONResponse(
                status_code=400,
                content={"error": "Query is required"}
            )
            
        response = agent_orchestrator.process_query(query)
        return {"response": response}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/api/update-knowledge")
async def update_knowledge():
    try:
        result = agent_orchestrator.update_knowledge_base()
        return {"status": "success", "result": result}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/api/traces")
async def get_traces():
    try:
        traces = agent_orchestrator.get_agent_traces()
        return {"traces": traces}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        ) 