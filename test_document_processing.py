#!/usr/bin/env python
"""
Test script for document processing functionality.
This script verifies that the application can download and process documents
from the Google Drive folder.
"""

import os
import sys
import json
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import pickle
import tempfile

# Load environment variables
load_dotenv()

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_google_drive_service():
    """Authenticate and build the Google Drive service."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH'), SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('drive', 'v3', credentials=creds)

def test_document_processing():
    """Test document processing by downloading and processing a sample document."""
    print("Testing document processing...")
    
    # Get Google Drive service
    service = get_google_drive_service()
    folder_id = os.getenv('REGULATIONS_FOLDER_ID')
    
    # List files in the regulations folder
    results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name, mimeType, modifiedTime)"
    ).execute()
    
    files = results.get('files', [])
    
    if not files:
        print("❌ No files found in the regulations folder")
        return False
    
    print(f"Found {len(files)} files in the regulations folder")
    
    # Find a PDF or DOCX file to test with
    test_file = None
    for file in files:
        if file['mimeType'] in ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            test_file = file
            break
    
    if not test_file:
        print("❌ No PDF or DOCX files found in the regulations folder")
        return False
    
    print(f"Testing with file: {test_file['name']} ({test_file['mimeType']})")
    
    # Download the file
    request = service.files().get_media(fileId=test_file['id'])
    file_content = io.BytesIO()
    downloader = MediaIoBaseDownload(file_content, request)
    
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    
    print("✅ Successfully downloaded the file")
    
    # Save the file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as temp_file:
        temp_file.write(file_content.getvalue())
        temp_path = temp_file.name
    
    print(f"✅ Saved file to temporary location: {temp_path}")
    
    # Process the file based on its type
    try:
        if test_file['mimeType'] == 'application/pdf':
            import pdfplumber
            with pdfplumber.open(temp_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                print(f"✅ Successfully extracted text from PDF ({len(text)} characters)")
                print("Sample text:")
                print(text[:200] + "..." if len(text) > 200 else text)
        
        elif test_file['mimeType'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            import docx
            doc = docx.Document(temp_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            print(f"✅ Successfully extracted text from DOCX ({len(text)} characters)")
            print("Sample text:")
            print(text[:200] + "..." if len(text) > 200 else text)
        
        # Clean up the temporary file
        os.unlink(temp_path)
        print("✅ Cleaned up temporary file")
        
        return True
    
    except Exception as e:
        print(f"❌ Error processing document: {str(e)}")
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        return False

if __name__ == "__main__":
    success = test_document_processing()
    if success:
        print("\n✅ Document processing test passed!")
        sys.exit(0)
    else:
        print("\n❌ Document processing test failed!")
        sys.exit(1) 