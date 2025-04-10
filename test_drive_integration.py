#!/usr/bin/env python
"""
Test script for Google Drive integration.
This script verifies that the application can authenticate with Google Drive
and access the regulations folder.
"""

import os
import sys
import json
import traceback
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# Load environment variables
load_dotenv()

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def test_google_drive_integration():
    """Test Google Drive integration by authenticating and listing files in the regulations folder."""
    print("Testing Google Drive integration...")
    
    # Check if credentials file exists
    credentials_path = os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH')
    if not os.path.exists(credentials_path):
        print(f"❌ Error: Credentials file not found at {credentials_path}")
        return False
    
    # Check if folder ID is set
    folder_id = os.getenv('REGULATIONS_FOLDER_ID')
    if not folder_id:
        print("❌ Error: REGULATIONS_FOLDER_ID not set in .env file")
        return False
    
    print(f"✅ Found credentials file: {credentials_path}")
    print(f"✅ Found folder ID: {folder_id}")
    
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
    
    # Authenticate with Google Drive
    creds = None
    if os.path.exists('token.pickle'):
        print("\nFound existing token, attempting to use it...")
        try:
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
            print("✅ Successfully loaded token from token.pickle")
        except Exception as e:
            print(f"❌ Error loading token.pickle: {str(e)}")
            print("Will attempt to create a new token.")
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("\nToken expired, refreshing...")
            try:
                creds.refresh(Request())
                print("✅ Successfully refreshed token")
            except Exception as e:
                print(f"❌ Error refreshing token: {str(e)}")
                print("Will attempt to create a new token.")
                creds = None
        else:
            print("\nNo valid token found, starting OAuth flow...")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                print("✅ Successfully created OAuth flow")
                print("Opening browser for authentication...")
                creds = flow.run_local_server(port=0)
                print("✅ Successfully obtained credentials from OAuth flow")
            except Exception as e:
                print(f"❌ Error during OAuth flow: {str(e)}")
                print("Detailed error:")
                traceback.print_exc()
                return False
        
        # Save the credentials for the next run
        if creds:
            try:
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
                print("✅ Successfully saved token to token.pickle")
            except Exception as e:
                print(f"❌ Error saving token: {str(e)}")
    
    if not creds:
        print("❌ Failed to obtain valid credentials")
        return False
    
    print("\n✅ Successfully authenticated with Google Drive")
    
    # Build the Drive API service
    try:
        service = build('drive', 'v3', credentials=creds)
        print("✅ Successfully built Drive API service")
    except Exception as e:
        print(f"❌ Error building Drive API service: {str(e)}")
        return False
    
    # List files in the regulations folder
    try:
        print(f"\nAttempting to list files in folder: {folder_id}")
        results = service.files().list(
            q=f"'{folder_id}' in parents",
            fields="files(id, name, mimeType, modifiedTime)"
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            print("❌ No files found in the regulations folder")
            return False
        
        print(f"✅ Successfully found {len(files)} files in the regulations folder:")
        for file in files:
            print(f"  - {file['name']} ({file['mimeType']})")
        
        return True
    
    except Exception as e:
        print(f"❌ Error listing files: {str(e)}")
        print("Detailed error:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_google_drive_integration()
    if success:
        print("\n✅ Google Drive integration test passed!")
        sys.exit(0)
    else:
        print("\n❌ Google Drive integration test failed!")
        sys.exit(1) 