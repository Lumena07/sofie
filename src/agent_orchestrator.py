"""
Agent Orchestrator for Sofie.
This module implements the OpenAI Agents SDK integration for Sofie.
"""

import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI
from src.knowledge_base import KnowledgeBase
from src.drive_integration import DriveIntegration
from src.document_processor import DocumentProcessor

# Load environment variables
load_dotenv()

class AgentOrchestrator:
    """Agent Orchestrator for Sofie using OpenAI Agents SDK."""
    
    def __init__(self):
        """Initialize the agent orchestrator."""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in .env file")
        
        self.client = OpenAI(api_key=self.openai_api_key)
        
        # Initialize components
        self.knowledge_base = KnowledgeBase()
        self.drive_integration = DriveIntegration()
        self.document_processor = DocumentProcessor()
        
        # Initialize agent
        self.agent_id = None
        self.initialize_agent()
    
    def initialize_agent(self):
        """Initialize the OpenAI agent."""
        try:
            # Create agent using OpenAI Agents SDK
            agent = self.client.agents.create(
                name="Sofie Aviation Assistant",
                description="An AI assistant specialized in Tanzanian aviation regulations",
                instructions="""
                You are Sofie, an AI assistant specialized in Tanzanian aviation regulations.
                Your primary function is to answer questions about aviation regulations in Tanzania.
                You should only answer questions related to aviation regulations.
                If a question is not related to aviation regulations, respond with:
                "I can only answer questions related to Tanzanian aviation regulations."
                
                When answering questions:
                1. Be accurate and concise
                2. Cite specific regulations when possible
                3. If you don't know the answer, say so
                4. If the information is not in the provided context, say so
                """,
                model="gpt-4",
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "query_knowledge_base",
                            "description": "Query the knowledge base for information about aviation regulations",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "The query to search for in the knowledge base"
                                    }
                                },
                                "required": ["query"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "update_knowledge_base",
                            "description": "Update the knowledge base with latest documents from Google Drive",
                            "parameters": {
                                "type": "object",
                                "properties": {}
                            }
                        }
                    }
                ]
            )
            
            self.agent_id = agent.id
            print(f"Agent initialized with ID: {self.agent_id}")
            
        except Exception as e:
            print(f"Error initializing agent: {str(e)}")
            # Fallback to direct knowledge base queries
            self.agent_id = None
    
    def process_query(self, query):
        """Process a query using the agent."""
        if not self.agent_id:
            # Fallback to direct knowledge base query
            return self.knowledge_base.query_knowledge_base(query)
        
        try:
            # Create a thread
            thread = self.client.threads.create()
            
            # Add the user's message to the thread
            self.client.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=query
            )
            
            # Run the agent on the thread
            run = self.client.threads.runs.create(
                thread_id=thread.id,
                agent_id=self.agent_id
            )
            
            # Wait for the run to complete
            while True:
                run_status = self.client.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                
                if run_status.status == "completed":
                    break
                elif run_status.status == "failed":
                    print(f"Run failed: {run_status.last_error}")
                    return {"answer": "I encountered an error while processing your query. Please try again later.", "confidence": 0.0}
                
                time.sleep(1)
            
            # Get the assistant's response
            messages = self.client.threads.messages.list(thread_id=thread.id)
            assistant_message = next((msg for msg in messages.data if msg.role == "assistant"), None)
            
            if assistant_message:
                return {
                    "answer": assistant_message.content[0].text.value,
                    "confidence": 0.8  # Default confidence for agent responses
                }
            else:
                return {"answer": "I couldn't generate a response. Please try again.", "confidence": 0.0}
                
        except Exception as e:
            print(f"Error processing query with agent: {str(e)}")
            # Fallback to direct knowledge base query
            return self.knowledge_base.query_knowledge_base(query)
    
    def update_knowledge_base(self):
        """Update the knowledge base with latest documents."""
        return self.knowledge_base.update_knowledge_base()
    
    def get_agent_traces(self):
        """Get traces of agent interactions for monitoring."""
        if not self.agent_id:
            return []
        
        try:
            traces = self.client.agents.traces.list(agent_id=self.agent_id)
            return traces.data
        except Exception as e:
            print(f"Error getting agent traces: {str(e)}")
            return [] 