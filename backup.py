#!/usr/bin/env python3
from __future__ import print_function
import pickle
import os.path
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class Backup:

    SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
    TOKEN_FILE = 'token.pickle'

    service = None

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

    def list_items(self, page_size=10):
        service = self.provide_service()
        results = service.files().list(orderBy="modifiedTime desc", pageSize=page_size, 
            q="mimeType != 'application/vnd.google-apps.folder'", 
            fields="nextPageToken, files(id, name, size, version, mimeType,originalFilename)").execute()
        return results.get('files', [])

    def download_file(self, file_id):
        service = self.provide_service()
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))

    def provide_service(self):
        if self.service is None:
            credentials = self.authorize()
            self.service = build('drive', 'v3', credentials=credentials)
        return self.service

def main():
    backup = Backup()

    items = backup.list_items(1)
    backup.download_file(items[0]['id'])

    for item in items:
        print(item)

if __name__ == '__main__':
    main()