#!/usr/bin/env python3
from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class Backup:

    SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
    TOKEN_FILE = 'token.pickle'

    def authorize(self):
        credentials = None
        
        if os.path.exists(self.TOKEN_FILE):
            with open(self.TOKEN_FILE, 'rb') as token:
                credentials = pickle.load(token)
            
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                credentials = flow.run_local_server(port=0)
            
            with open(self.TOKEN_FILE, 'wb') as token:
                pickle.dump(credentials, token)
        
        return credentials

    def list_items(self, credentials, page_size=10):
        service = self.build_service(credentials)
        results = service.files().list(orderBy="modifiedTime desc", q="mimeType != 'application/vnd.google-apps.folder'", fields="nextPageToken, files(id, name, size, version, mimeType,originalFilename)").execute()
        return results.get('files', [])

    def build_service(self, credentials):
        return build('drive', 'v3', credentials=credentials)

def main():
    backup = Backup()
    credentials = backup.authorize()

    items = backup.list_items(credentials, 3)

    for item in items:
        print(item)

if __name__ == '__main__':
    main()