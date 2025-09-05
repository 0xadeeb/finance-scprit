"""
Google Drive API implementation of cloud storage interface.
"""

import os
import io
import json
from typing import Optional, Dict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from google.oauth2 import service_account

from .base import CloudStorage


class GoogleDriveAPI(CloudStorage):
    """Google Drive implementation of cloud storage interface"""
    
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def __init__(self):
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Drive API"""
        creds = None
        
        # Try OAuth 2.0 first
        if os.path.exists('credentials.json'):
            # Check if we have saved credentials
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
            
            # If there are no (valid) credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', self.SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
        
        # Try Service Account authentication
        elif os.path.exists('service-account.json'):
            creds = service_account.Credentials.from_service_account_file(
                'service-account.json', scopes=self.SCOPES)
        
        else:
            raise FileNotFoundError(
                "No credentials found. Please add either 'credentials.json' or 'service-account.json' "
                "See SETUP_INSTRUCTIONS.md for details."
            )
        
        self.service = build('drive', 'v3', credentials=creds)
        print("✅ Successfully authenticated with Google Drive API")
    
    def get_provider_name(self) -> str:
        """Get the name of the cloud storage provider"""
        return "Google Drive"
    
    def list_files_in_folder(self, folder_id: str) -> Optional[list]:
        """List all files in a folder"""
        try:
            query = f"parents in '{folder_id}'"
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType, modifiedTime)"
            ).execute()
            items = results.get('files', [])
            
            print(f"✅ Listed {len(items)} files in folder {folder_id}")
            return items
        except Exception as e:
            print(f"❌ Error listing files in folder {folder_id}: {str(e)}")
            return None
    
    def download_content(self, file_id: str) -> Optional[str]:
        """Download file content directly as string"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_io = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            content = file_io.getvalue().decode('utf-8')
            print(f"✅ Downloaded file content (ID: {file_id})")
            return content
        except Exception as e:
            print(f"❌ Error downloading file content {file_id}: {str(e)}")
            return None
    
    def download_file(self, file_id: str, local_path: str) -> bool:
        """Download a file from Google Drive"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_io = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            with open(local_path, 'wb') as f:
                f.write(file_io.getvalue())
            
            print(f"✅ Downloaded: {local_path}")
            return True
        except Exception as e:
            print(f"❌ Error downloading file {file_id}: {str(e)}")
            return False
    
    def create_file(self, filename: str, content: str, parent_folder_id: str, mimetype: str = 'application/json') -> Optional[str]:
        """Create a new file in Google Drive"""
        try:
            file_metadata = {
                'name': filename,
                'parents': [parent_folder_id]
            }
            media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype=mimetype)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            print(f"✅ Created new file: {filename} (ID: {file.get('id')})")
            return file.get('id')
        except Exception as e:
            print(f"❌ Error creating file {filename}: {str(e)}")
            return None
    
    def upload_content(self, content: str, file_id: str, mimetype: str = 'application/json') -> bool:
        """Upload content directly to a file in Google Drive"""
        try:
            media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype=mimetype)
            
            self.service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
            
            print(f"✅ Updated file content (ID: {file_id})")
            return True
        except Exception as e:
            print(f"❌ Error updating file content {file_id}: {str(e)}")
            return False
    
    def upload_file(self, local_path: str, file_id: str) -> bool:
        """Upload/update a file to Google Drive"""
        try:
            # Open file and keep it open during the entire upload process
            with open(local_path, 'rb') as f:
                media = MediaIoBaseUpload(f, mimetype='application/octet-stream')
                
                # Perform the upload while the file is still open
                self.service.files().update(
                    fileId=file_id,
                    media_body=media
                ).execute()
            
            print(f"✅ Uploaded: {local_path}")
            return True
        except Exception as e:
            print(f"❌ Error uploading file {file_id}: {str(e)}")
            return False
    
    def find_file_in_folder(self, folder_id: str, filename: str) -> Optional[str]:
        """Find a file by name in a specific folder"""
        try:
            query = f"name='{filename}' and parents in '{folder_id}'"
            print(f"🔍 Searching with query: {query}")
            results = self.service.files().list(q=query).execute()
            items = results.get('files', [])
            
            if items:
                print(f"📁 Found {len(items)} file(s) matching '{filename}':")
                for item in items:
                    print(f"   - Name: {item.get('name', 'Unknown')}, ID: {item.get('id', 'Unknown')}")
                return items[0]['id']
            else:
                print(f"📁 No files found matching '{filename}' in folder {folder_id}")
            return None
        except Exception as e:
            print(f"❌ Error finding file {filename} in folder {folder_id}: {str(e)}")
            return None
