from io import BytesIO
from uuid import UUID

from minio import Minio

from math_rag.application.base.repositories.objects import ArticleBaseRepository
from math_rag.core.models import MathArticle


class MathArticleRepository(ArticleBaseRepository):
    def __init__(self, client: Minio):
        self.client = client
        self.bucket_name = MathArticle.__name__.lower()

    def insert_math_articles(self, math_articles: list[MathArticle]):
        for math_article in math_articles:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=math_article.name,
                data=math_article.bytes,
                length=math_article.bytes.getbuffer().nbytes,
                content_type='application/octet-stream',
                metadata={'X-Amz-Meta-id': str(math_article.id)},
            )

    def get_math_article_by_name(self, name: str) -> BytesIO:
        object_response = self.client.get_object(self.bucket_name, name)
        object_bytes = BytesIO(object_response.read())
        object_response.close()
        object_response.release_conn()

        stat_response = self.client.stat_object(self.bucket_name, name)
        id = stat_response.metadata.get('X-Amz-Meta-id')

        return MathArticle(id=UUID(id), name=name, bytes=object_bytes)

    def list_math_article_names(self) -> list[str]:
        objects = self.client.list_objects(self.bucket_name, recursive=True)

        return [
            object.object_name for object in objects if object.object_name is not None
        ]
