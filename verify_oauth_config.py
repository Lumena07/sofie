#!/usr/bin/env python
"""
OAuth Configuration Verification Script
This script helps verify your OAuth configuration for Google Drive API.
"""

import os
import sys
import json
import webbrowser
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# Load environment variables
load_dotenv()

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def verify_oauth_config():
    """Verify OAuth configuration for Google Drive API."""
    print("Verifying OAuth configuration for Google Drive API...")
    
    # Check if credentials file exists
    credentials_path = os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH')
    if not os.path.exists(credentials_path):
        print(f"❌ Error: Credentials file not found at {credentials_path}")
        return False
    
    print(f"✅ Found credentials file: {credentials_path}")
    
    # Print credentials file content (without sensitive parts)
    try:
        with open(credentials_path, 'r') as f:
            creds_data = json.load(f)
            print("\nCredentials file content (sanitized):")
            print(f"  client_id: {creds_data.get('client_id', 'Not found')}")
            print(f"  project_id: {creds_data.get('project_id', 'Not found')}")
            print(f"  auth_uri: {creds_data.get('auth_uri', 'Not found')}")
            print(f"  token_uri: {creds_data.get('token_uri', 'Not found')}")
            print(f"  auth_provider_x509_cert_url: {creds_data.get('auth_provider_x509_cert_url', 'Not found')}")
            print(f"  redirect_uris: {creds_data.get('redirect_uris', 'Not found')}")
            print(f"  client_secret: {'[REDACTED]' if 'client_secret' in creds_data else 'Not found'}")
    except Exception as e:
        print(f"❌ Error reading credentials file: {str(e)}")
        return False
    
    # Check if token.pickle exists
    if os.path.exists('token.pickle'):
        print("\nFound existing token.pickle file.")
        try:
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
            print("✅ Successfully loaded token from token.pickle")
            
            # Check if token is valid
            if creds.valid:
                print("✅ Token is valid")
                return True
            elif creds.expired and creds.refresh_token:
                print("⚠️ Token is expired but has refresh token")
                try:
                    creds.refresh(Request())
                    print("✅ Successfully refreshed token")
                    return True
                except Exception as e:
                    print(f"❌ Error refreshing token: {str(e)}")
            else:
                print("❌ Token is invalid and cannot be refreshed")
        except Exception as e:
            print(f"❌ Error loading token.pickle: {str(e)}")
    
    # Try to create a new token
    print("\nAttempting to create a new token...")
    try:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        print("✅ Successfully created OAuth flow")
        
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
        creds = flow.run_local_server(port=0)
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
    success = verify_oauth_config()
    if success:
        print("\n✅ OAuth configuration verification passed!")
        sys.exit(0)
    else:
        print("\n❌ OAuth configuration verification failed!")
        sys.exit(1) 