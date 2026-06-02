import os
import streamlit as st
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

def get_drive_service():
    """Authenticate and return the Google Drive service object using OAuth Token from secrets."""
    try:
        # Load credentials dictionary from Streamlit Secrets
        token_info = dict(st.secrets["gcp_oauth_token"])
        creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                raise Exception("OAuth token is invalid.")
                
        service = build("drive", "v3", credentials=creds)
        return service
    except KeyError:
        raise Exception("OAuth credentials not found in Streamlit secrets. Please configure .streamlit/secrets.toml or Cloud Secrets.")
    except Exception as err:
        print(f"An error occurred initializing Drive service: {err}")
        raise err

def get_or_create_folder(service, folder_name, parent_id=None):
    """Search for a folder by name. If it doesn't exist, create it."""
    try:
        # Search for the folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
            
        response = service.files().list(q=query, spaces='drive', fields='nextPageToken, files(id, name)').execute()
        files = response.get('files', [])

        if not files:
            # Folder doesn't exist, create it
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                folder_metadata['parents'] = [parent_id]
                
            folder = service.files().create(body=folder_metadata, fields='id').execute()
            return folder.get('id')
        else:
            # Return the first found folder's ID
            return files[0].get('id')

    except Exception as err:
        print(f"An error occurred in get_or_create_folder: {err}")
        raise err

def upload_file_to_drive(service, file_obj, file_name, folder_id, mime_type=None):
    """Upload an in-memory file to a specific Google Drive folder."""
    try:
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        
        media = MediaIoBaseUpload(file_obj, mimetype=mime_type, resumable=True)
        
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        
        return file.get('id'), file.get('webViewLink')

    except Exception as err:
        print(f"An error occurred in upload_file_to_drive: {err}")
        raise err
