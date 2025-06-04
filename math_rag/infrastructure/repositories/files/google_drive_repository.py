from io import BytesIO
from logging import getLogger
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from googleapiclient.http import MediaIoBaseDownload


logger = getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive']


class GoogleDriveRepository:
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

    def get_file_id(self, file_path: Path) -> str | None:
        folders = file_path.parent
        target_name = file_path.name

        parent_id = 'root'

        if folders != Path('.'):
            for segment in folders.parts:
                folder_query = (
                    f"name='{segment}' "
                    f"and mimeType='application/vnd.google-apps.folder' "
                    f"and '{parent_id}' in parents"
                )
                folder_results: dict = (
                    self.resource.files().list(q=folder_query, fields='files(id, name)').execute()
                )
                subfolders = folder_results.get('files', [])

                if not subfolders:
                    logger.info(f"Folder '{segment}' not found under parent ID '{parent_id}'")
                    return None

                parent_id = subfolders[0]['id']

        file_query = f"name='{target_name}' and '{parent_id}' in parents"
        file_results: dict = (
            self.resource.files().list(q=file_query, fields='files(id, name)').execute()
        )
        matches = file_results.get('files', [])

        if not matches:
            logger.info(f"File '{target_name}' not found under '{folders}'")
            return None

        return matches[0]['id']

    def get_file_by_id(self, file_id: str) -> BytesIO:
        request = self.resource.files().get_media(fileId=file_id)
        file_bytes = BytesIO()

        downloader = MediaIoBaseDownload(file_bytes, request)
        done = False

        while not done:
            _, done = downloader.next_chunk(num_retries=3)

        return file_bytes
