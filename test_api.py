import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = "https://sofie-sage.vercel.app"

# Test queries that should use knowledge base
TEST_QUERIES = [
    "What are the key points about fatigue risk management?",
    "What are the requirements for pilot rest periods in Tanzania?",
    "What is the maximum duty time for pilots according to Tanzanian regulations?"
]

def test_endpoint(endpoint, method="GET", data=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    print(f"\nTesting {endpoint}...")
    print(f"Method: {method}")
    print(f"URL: {url}")
    if data:
        print(f"Query: {data.get('query', '')}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        else:
            response = requests.post(url, headers=headers, json=data)
        
        print(f"Status: {response.status_code}")
        print("Response:", response.text)
        
        if response.status_code == 200:
            try:
                print("Parsed JSON Response:", json.dumps(response.json(), indent=2))
            except:
                print("Response is not JSON")
        
        return response
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def main():
    print("Testing API with aviation-specific queries...")
    
    # Test each query
    for query in TEST_QUERIES:
        test_endpoint("/api/query", method="POST", data={"query": query})
        print("\n" + "="*50)  # Separator between queries

if __name__ == "__main__":
    main() 