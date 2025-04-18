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
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not set correctly in .env file")
        return False
    
    # Check if Google Drive credentials are set
    credentials = os.getenv('GOOGLE_DRIVE_CREDENTIALS')
    folder_id = os.getenv('REGULATIONS_FOLDER_ID')
    
    if not credentials or not folder_id:
        print("❌ Error: Google Drive credentials not set correctly")
        return False
    
    print("✅ Found all required credentials")
    
    # Save credentials to a temporary file
    try:
        with open('temp_credentials.json', 'w') as f:
            f.write(credentials)
        os.environ['GOOGLE_DRIVE_CREDENTIALS_PATH'] = 'temp_credentials.json'
    except Exception as e:
        print(f"❌ Error saving credentials: {str(e)}")
        return False
    
    # Initialize the knowledge base
    try:
        kb = KnowledgeBase()
        print("✅ Successfully initialized knowledge base")
    except Exception as e:
        print(f"❌ Error initializing knowledge base: {str(e)}")
        return False
    finally:
        # Clean up temporary credentials file
        if os.path.exists('temp_credentials.json'):
            os.remove('temp_credentials.json')
    
    # Test querying the knowledge base
    try:
        print("\nTesting knowledge base query...")
        query = "What documents do you have about aviation regulations in Tanzania?"
        print(f"Query: {query}")
        
        response = kb.query_knowledge_base(query)
        
        print("✅ Successfully queried knowledge base")
        print("\nResponse:")
        print("-" * 50)
        print(response['answer'])
        print("-" * 50)
        print(f"Confidence: {response['confidence']:.2f}")
        
        # Test another query
        print("\nTesting specific regulation query...")
        query = "What are the fatigue risk management requirements?"
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