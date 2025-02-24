from minio import Minio

from math_rag.application.base.seeders.objects import ArticleBaseSeeder
from math_rag.core.models import MathArticle


class MathArticleSeeder(ArticleBaseSeeder):
    def __init__(self, client: Minio):
        self.client = client
        self.bucket_name = MathArticle.__name__.lower()

    def seed(self, reset=True):
        if reset:
            self._delete_bucket()

        self._create_bucket()

    def _create_bucket(self):
        if self.client.bucket_exists(self.bucket_name):
            return

        self.client.make_bucket(self.bucket_name)

    def _delete_bucket(self):
        if not self.client.bucket_exists(self.bucket_name):
            return

        objects = self.client.list_objects(self.bucket_name, recursive=True)

        for object in objects:
            self.client.remove_object(self.bucket_name, object.object_name)

        self.client.remove_bucket(self.bucket_name)
