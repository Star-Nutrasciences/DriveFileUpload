import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Requesting the full Drive scope so the app can see folders you created manually
SCOPES = ["https://www.googleapis.com/auth/drive"]

def reauthenticate():
    # Remove the old restricted token if it exists
    if os.path.exists('token.json'):
        os.remove('token.json')
        
    print("Initiating new authentication flow using credentials.json...")
    
    # Use the official credentials file
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    
    # Run the local server to prompt the user on port 8080 (must match credentials.json)
    creds = flow.run_local_server(port=8080)

    # Save the new token with full access
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
        
    print("✅ Authentication successful! The new token.json has been saved with full Drive access.")

if __name__ == '__main__':
    reauthenticate()
