import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

def get_drive_service(token_path='token.json'):
    """Authenticate and return the Google Drive service object."""
    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If there are no (valid) credentials available, attempt to refresh.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("token.json not found or invalid. Please ensure token.json with valid credentials exists.")
            
    try:
        service = build("drive", "v3", credentials=creds)
        return service
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

def upload_file_to_drive(service, file_path, folder_id, mime_type=None):
    """Upload a file to a specific Google Drive folder."""
    try:
        file_name = os.path.basename(file_path)
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
        
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        
        return file.get('id'), file.get('webViewLink')

    except Exception as err:
        print(f"An error occurred in upload_file_to_drive: {err}")
        raise err
