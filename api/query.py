from http.server import BaseHTTPRequestHandler
from src.agent_orchestrator import AgentOrchestrator
import json

def handler(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            query = body.get("query")
            
            if not query:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Query is required"})
                }
            
            agent = AgentOrchestrator()
            result = agent.process_query(query)
            
            return {
                "statusCode": 200,
                "body": json.dumps(result)
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