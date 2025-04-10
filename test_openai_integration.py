#!/usr/bin/env python
"""
Test script for OpenAI integration.
This script verifies that the application can connect to OpenAI's API
and generate responses using GPT models.
"""

import os
import sys
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

def test_openai_integration():
    """Test OpenAI integration by generating a simple response."""
    print("Testing OpenAI integration...")
    
    # Check if OpenAI API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not set in .env file")
        return False
    
    if api_key == "your_openai_api_key_here":
        print("❌ Error: OPENAI_API_KEY is still set to the default value")
        print("Please update your .env file with your actual OpenAI API key")
        return False
    
    print("✅ Found OpenAI API key")
    
    # Set the API key
    openai.api_key = api_key
    
    # Test the API with a simple query
    try:
        print("\nSending a test query to OpenAI...")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What are the key components of aviation regulations?"}
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        # Extract the response text
        response_text = response.choices[0].message.content
        
        print("✅ Successfully received response from OpenAI")
        print("\nSample response:")
        print("-" * 50)
        print(response_text)
        print("-" * 50)
        
        return True
    
    except Exception as e:
        print(f"❌ Error connecting to OpenAI: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_openai_integration()
    if success:
        print("\n✅ OpenAI integration test passed!")
        sys.exit(0)
    else:
        print("\n❌ OpenAI integration test failed!")
        sys.exit(1) 