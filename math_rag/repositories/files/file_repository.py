from minio import Minio

from math_rag.core.base import BaseFileRepository


class FileRepository(BaseFileRepository):
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
