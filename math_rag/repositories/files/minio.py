from minio import Minio

from math_rag.core.base import FileRepository


class MinioRepository(FileRepository):
    def __init__(self):
        self.client = Minio(
            endpoint='play.min.io',
            access_key='Q3AM3UQ867SPQQA43P2F',
            secret_key='zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG',
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
