from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import os
import pickle
from .config import settings

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class GoogleDriveService:
    def __init__(self):
        self.creds = None
        self.service = None

    def authenticate(self):
        """Authenticate with Google Drive API."""
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.google_drive_credentials_path, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('drive', 'v3', credentials=self.creds)

    def list_files_in_folder(self, folder_id):
        """List all files in the specified folder."""
        if not self.service:
            self.authenticate()

        results = self.service.files().list(
            q=f"'{folder_id}' in parents",
            fields="files(id, name, mimeType, modifiedTime)"
        ).execute()
        
        return results.get('files', [])

    def download_file(self, file_id):
        """Download a file from Google Drive."""
        if not self.service:
            self.authenticate()

        request = self.service.files().get_media(fileId=file_id)
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()

        return file_content.getvalue()

    def get_latest_files(self, folder_id, file_types=None):
        """Get the latest version of files in the folder."""
        files = self.list_files_in_folder(folder_id)
        
        if file_types:
            files = [f for f in files if f['mimeType'] in file_types]
        
        # Sort by modified time
        files.sort(key=lambda x: x['modifiedTime'], reverse=True)
        
        return files 