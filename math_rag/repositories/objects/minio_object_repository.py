from io import BytesIO

from minio import Minio

from math_rag.application.base.repositories.objects import ObjectBaseRepository


class MinioObjectRepository(ObjectBaseRepository):
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

        for object in objects:
            self.client.remove_object(name, object.object_name)

        self.client.remove_bucket(name)

    def insert_object(self, bucket_name: str, object_name: str, object_bytes: BytesIO):
        self.client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=object_bytes,
            length=object_bytes.getbuffer().nbytes,
            content_type='application/octet-stream',
        )

    def get_object(self, bucket_name: str, object_name: str) -> BytesIO:
        response = self.client.get_object(bucket_name, object_name)
        object_bytes = BytesIO(response.read())
        response.close()
        response.release_conn()

        return object_bytes

    def list_object_names(self, bucket_name: str) -> list[str]:
        objects = self.client.list_objects(bucket_name, recursive=True)

        return [
            object.object_name for object in objects if object.object_name is not None
        ]

    def clear_bucket(self, bucket_name: str):
        object_names = self.list_object_names(bucket_name)

        if object_names:
            self.client.remove_objects(bucket_name, object_names)
