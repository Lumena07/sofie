import requests
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

# Debug: Check if API key is loaded
api_key = os.getenv('OPENAI_API_KEY')
print(f"API Key loaded: {'Yes' if api_key else 'No'}")
print(f"API Key length: {len(api_key) if api_key else 0}")

# Test root endpoint
print("\nTesting root endpoint...")
try:
    response = requests.get('https://sofie-sage.vercel.app/api/query/')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {str(e)}")

# Test query endpoint
print("\nTesting query endpoint...")
try:
    response = requests.post(
        'https://sofie-sage.vercel.app/api/query',
        json={'query': 'test'},
        headers={'Content-Type': 'application/json'}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {str(e)}")

try:
    # Prepare request data
    url = 'https://sofie-sage.vercel.app/api/query'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'query': 'Summarize the new Fatique Risk regulations for an airline'
    }

    # Debug: Print request details
    print("\nRequest Details:")
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Data: {json.dumps(data, indent=2)}")

    # Make the request
    print("\nMaking request...")
    response = requests.post(url, json=data, headers=headers)
    
    # Debug: Print response details
    print("\nResponse Details:")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
    print(f"Response Body: {response.text}")

    # Try to parse JSON response
    try:
        json_response = response.json()
        print(f"\nParsed JSON Response: {json.dumps(json_response, indent=2)}")
    except json.JSONDecodeError as e:
        print(f"\nCould not parse response as JSON: {str(e)}")

except requests.exceptions.RequestException as e:
    print(f"\nRequest Error: {str(e)}")
except Exception as e:
    print(f"\nUnexpected Error: {str(e)}") 