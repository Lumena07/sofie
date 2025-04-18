#!/usr/bin/env python
"""
Script to update the knowledge base with documents from Google Drive.
This script will:
1. Initialize the knowledge base
2. Download and process all documents
3. Create embeddings for semantic search
4. Save the vector store
"""

import os
from dotenv import load_dotenv
from src.knowledge_base import KnowledgeBase

# Load environment variables
load_dotenv()

def main():
    """Update the knowledge base."""
    print("Initializing knowledge base...")
    try:
        kb = KnowledgeBase()
        print("✅ Knowledge base initialized successfully")
        
        print("\nUpdating knowledge base with documents...")
        num_documents = kb.update_knowledge_base()
        print(f"✅ Successfully processed {num_documents} documents")
        
        print("\nKnowledge base update complete!")
        print(f"Vector store saved to: {kb.vector_store_path}")
        
    except Exception as e:
        print(f"❌ Error updating knowledge base: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Knowledge base update completed successfully!")
    else:
        print("\n❌ Knowledge base update failed!") 