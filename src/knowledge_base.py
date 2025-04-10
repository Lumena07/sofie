"""
Knowledge base manager for Sofie.
This module handles the knowledge base for the Sofie application.
"""

import os
import json
import pickle
import numpy as np
from dotenv import load_dotenv
import openai
from src.document_processor import DocumentProcessor
from src.drive_integration import DriveIntegration

# Load environment variables
load_dotenv()

class KnowledgeBase:
    """Knowledge base manager for Sofie."""
    
    def __init__(self):
        """Initialize the knowledge base."""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in .env file")
        
        openai.api_key = self.openai_api_key
        
        self.document_processor = DocumentProcessor()
        self.drive_integration = DriveIntegration()
        
        # Initialize vector store for semantic search
        self.vector_store = {}
        self.vector_store_path = "vector_store.pkl"
        
        # Load existing vector store if available
        if os.path.exists(self.vector_store_path):
            with open(self.vector_store_path, 'rb') as f:
                self.vector_store = pickle.load(f)
    
    def update_knowledge_base(self):
        """Update the knowledge base with documents from Google Drive."""
        # Get documents from Google Drive
        documents = self.drive_integration.list_files()
        
        # Process documents
        processed_documents = []
        for doc in documents:
            try:
                content = self.drive_integration.download_file(doc['id'])
                processed_content = self.document_processor.process_document(content)
                processed_documents.append({
                    'id': doc['id'],
                    'name': doc['name'],
                    'content': processed_content
                })
            except Exception as e:
                print(f"Error processing document {doc['name']}: {str(e)}")
        
        # Update vector store
        self._update_vector_store(processed_documents)
        
        return len(processed_documents)
    
    def _update_vector_store(self, documents):
        """Update the vector store with new documents."""
        for doc in documents:
            # Generate embeddings for document content
            try:
                embedding = self._get_embedding(doc['content'])
                self.vector_store[doc['id']] = {
                    'name': doc['name'],
                    'content': doc['content'],
                    'embedding': embedding
                }
            except Exception as e:
                print(f"Error generating embedding for {doc['name']}: {str(e)}")
        
        # Save vector store
        with open(self.vector_store_path, 'wb') as f:
            pickle.dump(self.vector_store, f)
    
    def _get_embedding(self, text):
        """Get embedding for text using OpenAI API."""
        response = openai.Embedding.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def query_knowledge_base(self, query):
        """Query the knowledge base with a question."""
        # Get embedding for query
        query_embedding = self._get_embedding(query)
        
        # Find most relevant documents
        relevant_docs = self._find_relevant_documents(query_embedding, top_k=3)
        
        # Prepare context from relevant documents
        context = self._prepare_context(relevant_docs)
        
        # Apply guardrails to query
        safe_query = self._apply_guardrails(query)
        
        # Query OpenAI with context and safe query
        response = self._query_openai(safe_query, context)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(response, relevant_docs)
        
        return {
            'answer': response,
            'confidence': confidence
        }
    
    def _find_relevant_documents(self, query_embedding, top_k=3):
        """Find most relevant documents using cosine similarity."""
        if not self.vector_store:
            return []
        
        similarities = []
        for doc_id, doc_data in self.vector_store.items():
            similarity = self._cosine_similarity(query_embedding, doc_data['embedding'])
            similarities.append((doc_id, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top k documents
        return [self.vector_store[doc_id] for doc_id, _ in similarities[:top_k]]
    
    def _cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors."""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def _prepare_context(self, relevant_docs):
        """Prepare context from relevant documents."""
        context = ""
        for doc in relevant_docs:
            context += f"Document: {doc['name']}\n\n{doc['content']}\n\n"
        return context
    
    def _apply_guardrails(self, query):
        """Apply guardrails to query to prevent harmful or irrelevant responses."""
        # Check if query is related to aviation regulations
        system_prompt = """
        You are an AI assistant specialized in Tanzanian aviation regulations.
        Only answer questions related to aviation regulations in Tanzania.
        If the question is not related to aviation regulations, respond with:
        "I can only answer questions related to Tanzanian aviation regulations."
        """
        
        # Use moderation API to check for harmful content
        try:
            moderation_response = openai.Moderation.create(input=query)
            if moderation_response.results[0].flagged:
                return "I cannot answer this question due to content guidelines."
        except Exception as e:
            print(f"Error applying moderation: {str(e)}")
        
        return query
    
    def _query_openai(self, query, context):
        """Query OpenAI with context and query."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI assistant specialized in Tanzanian aviation regulations. Answer questions based on the provided context. If the answer cannot be found in the context, say so."},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
                ],
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error querying OpenAI: {str(e)}")
            return "I encountered an error while processing your query. Please try again later."
    
    def _calculate_confidence(self, response, relevant_docs):
        """Calculate confidence score for the response."""
        if not relevant_docs:
            return 0.0
        
        # Simple confidence calculation based on number of relevant documents
        # and whether the response indicates no information was found
        if "cannot be found in the context" in response or "no information" in response:
            return 0.3
        
        # Higher confidence if we have more relevant documents
        return min(0.3 + (len(relevant_docs) * 0.2), 0.9) 