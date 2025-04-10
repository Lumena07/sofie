#!/usr/bin/env python
"""
Test script for knowledge base functionality.
This script verifies that the knowledge base can process documents
and answer questions using OpenAI.
"""

import os
import sys
import json
from dotenv import load_dotenv
from src.knowledge_base import KnowledgeBase

# Load environment variables
load_dotenv()

def test_knowledge_base():
    """Test knowledge base functionality."""
    print("Testing knowledge base functionality...")
    
    # Check if OpenAI API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ Error: OPENAI_API_KEY not set correctly in .env file")
        return False
    
    # Check if Google Drive credentials are set
    credentials_path = os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH')
    folder_id = os.getenv('REGULATIONS_FOLDER_ID')
    
    if not os.path.exists(credentials_path) or folder_id == "your_folder_id_here":
        print("❌ Error: Google Drive credentials not set correctly")
        return False
    
    print("✅ Found all required credentials")
    
    # Initialize the knowledge base
    try:
        kb = KnowledgeBase()
        print("✅ Successfully initialized knowledge base")
    except Exception as e:
        print(f"❌ Error initializing knowledge base: {str(e)}")
        return False
    
    # Update the knowledge base
    try:
        print("\nUpdating knowledge base...")
        kb.update_knowledge_base()
        print("✅ Successfully updated knowledge base")
    except Exception as e:
        print(f"❌ Error updating knowledge base: {str(e)}")
        return False
    
    # Test querying the knowledge base
    try:
        print("\nTesting knowledge base query...")
        query = "What are the requirements for pilot licensing in Tanzania?"
        print(f"Query: {query}")
        
        response = kb.query_knowledge_base(query)
        
        print("✅ Successfully queried knowledge base")
        print("\nResponse:")
        print("-" * 50)
        print(response['answer'])
        print("-" * 50)
        print(f"Confidence: {response['confidence']:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Error querying knowledge base: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_knowledge_base()
    if success:
        print("\n✅ Knowledge base test passed!")
        sys.exit(0)
    else:
        print("\n❌ Knowledge base test failed!")
        sys.exit(1) 