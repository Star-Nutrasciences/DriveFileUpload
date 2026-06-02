from drive_utils import get_drive_service
import sys

def test():
    service = get_drive_service()
    parent_id = "14AZi6h0F_Wb4sV70Nexhxl-oaeK8vnrX"
    try:
        folder = service.files().get(fileId=parent_id, fields="id, name").execute()
        print(f"Successfully accessed parent folder: {folder['name']}")
        
        # Now try to search inside it
        query = f"'{parent_id}' in parents and trashed=false"
        response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        files = response.get('files', [])
        print(f"Found {len(files)} items inside it:")
        for f in files:
            print(f" - {f['name']} ({f['id']})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test()
