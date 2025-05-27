from io import BytesIO
from logging import getLogger
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from googleapiclient.http import MediaIoBaseDownload

from math_rag.application.base.repositories.files import BaseFileRepository


logger = getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive']


class GoogleFileRepository(BaseFileRepository):
    def __init__(self, resource: Resource):
        self.resource = resource

    @staticmethod
    def get_resource(credentials_path: Path, token_path: Path) -> Resource:
        credentials: Credentials | None = None

        if token_path.exists():
            credentials = Credentials.from_authorized_user_file(str(token_path), SCOPES)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())

            else:
                flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
                credentials = flow.run_local_server(port=0)

            token_path.write_text(credentials.to_json())

        return build('drive', 'v3', credentials=credentials)

    def get_file_id(self, file_name: str, folder_name: str) -> str | None:
        folder_query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
        folder_fields = 'files(id, name)'
        folder_results: dict = (
            self.resource.files().list(q=folder_query, fields=folder_fields).execute()
        )
        folders = folder_results.get('files', [])

        if not folders:
            logger.info(f'Folder {folder_name} not found')
            return None

        folder_id = folders[0]['id']

        file_query = f"name='{file_name}' and '{folder_id}' in parents"
        file_fields = 'files(id, name)'
        file_results: dict = self.resource.files().list(q=file_query, fields=file_fields).execute()
        files = file_results.get('files', [])

        if not files:
            logger.info(f'File {file_name} not found in directory {folder_name}')
            return None

        return files[0]['id']

    def get_file_by_id(self, file_id: str) -> BytesIO:
        request = self.resource.files().get_media(fileId=file_id)
        file_bytes = BytesIO()

        downloader = MediaIoBaseDownload(file_bytes, request)
        done = False

        while not done:
            _, done = downloader.next_chunk(num_retries=3)

        return file_bytes
