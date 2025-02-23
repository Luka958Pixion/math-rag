from io import BytesIO

from minio import Minio

from math_rag.application.base.repositories import FileBaseRepository


class MinioFileRepository(FileBaseRepository):
    def __init__(self, endpoint: str, access_key: str, secret_key: str):
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False,
        )

    def create_bucket(self, name: str):
        if self.client.bucket_exists(name):
            return

        self.client.make_bucket(name)

    def delete_bucket(self, name: str):
        objects = self.client.list_objects(name, recursive=True)

        for obj in objects:
            self.client.remove_object(name, obj.object_name)

        self.client.remove_bucket(name)

    def insert_file(self, bucket_name: str, file_name: str, file_bytes: BytesIO):
        self.client.put_object(
            bucket_name=bucket_name,
            object_name=file_name,
            data=file_bytes,
            length=file_bytes.getbuffer().nbytes,
            content_type='application/octet-stream',
        )
