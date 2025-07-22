from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import io
from dotenv import load_dotenv

load_dotenv()
# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# 폴더 ID와 저장 경로
FOLDER_ID = os.environ.get('GOOGLE_DRIVE_FOLDER_ID')
SAVE_DIR = os.environ.get('SAVE_DIR')
GOOGLE_OAUTH_CLIENT_SECRET_FILE = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET_FILE')

def main():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GOOGLE_OAUTH_CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('drive', 'v3', credentials=creds)

    # 폴더 내 파일 리스트 가져오기
    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents",
        pageSize=100, fields="files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        for item in items:
            file_id = item['id']
            file_name = "KakaoTalk_latest.txt"
            request = service.files().get_media(fileId=file_id)
            fh = io.FileIO(os.path.join(SAVE_DIR, file_name), 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f"Downloading {file_name} {int(status.progress() * 100)}%.")

if __name__ == "__main__":
    main()
