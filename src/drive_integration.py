"""
Google Drive integration for Sofie.
This module handles the integration with Google Drive API.
"""

import os
import json
import io
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import pickle

# Load environment variables
load_dotenv()

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class DriveIntegration:
    """Google Drive integration for Sofie."""
    
    def __init__(self):
        """Initialize the Google Drive integration."""
        self.creds = None
        self.service = None
        self.folder_id = os.getenv('REGULATIONS_FOLDER_ID')
        if not self.folder_id:
            raise ValueError("REGULATIONS_FOLDER_ID not set in .env file")
        
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Drive API."""
        # Check if token.pickle exists
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        # If credentials are not valid or don't exist
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # Get credentials from environment variable
                credentials_json = os.getenv('GOOGLE_DRIVE_CREDENTIALS')
                if not credentials_json:
                    raise ValueError("GOOGLE_DRIVE_CREDENTIALS not set in environment variables")
                
                # Create credentials from JSON string
                credentials_dict = json.loads(credentials_json)
                flow = InstalledAppFlow.from_client_config(credentials_dict, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        # Build the service
        self.service = build('drive', 'v3', credentials=self.creds)
    
    def list_files(self):
        """List files in the regulations folder."""
        try:
            results = self.service.files().list(
                q=f"'{self.folder_id}' in parents and trashed=false",
                fields="files(id, name, mimeType)"
            ).execute()
            
            return results.get('files', [])
        except Exception as e:
            print(f"Error listing files: {str(e)}")
            return []
    
    def download_file(self, file_id):
        """Download a file from Google Drive."""
        try:
            # Get file metadata to determine MIME type
            file_metadata = self.service.files().get(
                fileId=file_id,
                fields='mimeType'
            ).execute()
            mime_type = file_metadata.get('mimeType', 'application/octet-stream')
            
            # Download file content
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            return fh.getvalue(), mime_type
        except Exception as e:
            print(f"Error downloading file: {str(e)}")
            return None, None

    def list_files_in_folder(self, folder_id):
        """List all files in the specified folder."""
        if not self.service:
            self._authenticate()

        results = self.service.files().list(
            q=f"'{folder_id}' in parents",
            fields="files(id, name, mimeType, modifiedTime)"
        ).execute()
        
        return results.get('files', [])

    def get_latest_files(self, folder_id, file_types=None):
        """Get the latest version of files in the folder."""
        files = self.list_files_in_folder(folder_id)
        
        if file_types:
            files = [f for f in files if f['mimeType'] in file_types]
        
        # Sort by modified time
        files.sort(key=lambda x: x['modifiedTime'], reverse=True)
        
        return files 