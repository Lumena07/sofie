#!/usr/bin/env python
"""
OAuth Fix Script
This script helps fix OAuth issues by using a specific port for the redirect URI.
"""

import os
import sys
import json
import webbrowser
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

# Load environment variables
load_dotenv()

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def fix_oauth():
    """Fix OAuth by using a specific port for the redirect URI."""
    print("Fixing OAuth configuration...")
    
    # Check if credentials file exists
    credentials_path = os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH')
    if not os.path.exists(credentials_path):
        print(f"❌ Error: Credentials file not found at {credentials_path}")
        return False
    
    print(f"✅ Found credentials file: {credentials_path}")
    
    # Delete existing token.pickle if it exists
    if os.path.exists('token.pickle'):
        print("Deleting existing token.pickle file...")
        os.remove('token.pickle')
        print("✅ Deleted token.pickle")
    
    # Try to create a new token with a specific port
    print("\nAttempting to create a new token with a specific port...")
    try:
        # Create a flow with a specific port
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path, 
            SCOPES,
            redirect_uri='http://localhost:50421'
        )
        print("✅ Successfully created OAuth flow with specific redirect URI")
        
        # Open the OAuth consent screen in a browser
        print("\nOpening browser for authentication...")
        print("If the browser doesn't open automatically, please copy and paste the URL below into your browser:")
        
        # Get the authorization URL
        auth_url, _ = flow.authorization_url(prompt='consent')
        print(f"\n{auth_url}\n")
        
        # Try to open the browser
        try:
            webbrowser.open(auth_url)
        except:
            print("Could not open browser automatically. Please use the URL above.")
        
        # Ask user if they want to proceed
        response = input("Have you completed the authentication in your browser? (y/n): ")
        if response.lower() != 'y':
            print("Authentication cancelled by user")
            return False
        
        # Exchange the authorization code for credentials
        print("\nExchanging authorization code for credentials...")
        creds = flow.run_local_server(port=50421)
        print("✅ Successfully obtained credentials from OAuth flow")
        
        # Save the credentials
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        print("✅ Successfully saved token to token.pickle")
        
        return True
    
    except Exception as e:
        print(f"❌ Error during OAuth flow: {str(e)}")
        return False

if __name__ == "__main__":
    success = fix_oauth()
    if success:
        print("\n✅ OAuth fix successful!")
        sys.exit(0)
    else:
        print("\n❌ OAuth fix failed!")
        sys.exit(1) 