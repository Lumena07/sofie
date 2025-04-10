from http.server import BaseHTTPRequestHandler
from src.agent_orchestrator import AgentOrchestrator
import json

def handler(request):
    if request.method == "POST":
        try:
            agent = AgentOrchestrator()
            num_docs = agent.update_knowledge_base()
            
            return {
                "statusCode": 200,
                "body": json.dumps({"message": f"Updated {num_docs} documents"})
            }
            
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(e)})
            }
    else:
        return {
            "statusCode": 405,
            "body": json.dumps({"error": "Method not allowed"})
        } 