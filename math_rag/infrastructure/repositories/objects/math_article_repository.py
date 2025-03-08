from io import BytesIO

from minio import Minio

from math_rag.application.base.repositories.objects import BaseArticleRepository
from math_rag.core.models import MathArticle
from math_rag.infrastructure.mappings.objects import MathArticleMapping
from math_rag.infrastructure.models.objects import MathArticleObject


class MathArticleRepository(BaseArticleRepository):
    def __init__(self, client: Minio):
        self.client = client
        self.bucket_name = MathArticleObject.__name__.lower()

    def insert_many(self, items: list[MathArticle]):
        objs = [MathArticleMapping.to_target(item) for item in items]

        for obj in objs:
            data = BytesIO(obj.bytes)
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=obj.name,
                data=data,
                length=data.getbuffer().nbytes,
                content_type='application/octet-stream',
                metadata={'X-Amz-Meta-id': obj.id},
                num_parallel_uploads=1,
            )

    def find_by_name(self, name: str) -> MathArticle:
        object_response = self.client.get_object(self.bucket_name, name)
        object_bytes = BytesIO(object_response.read())
        object_response.close()
        object_response.release_conn()

        stat_response = self.client.stat_object(self.bucket_name, name)
        id = stat_response.metadata.get('X-Amz-Meta-id')

        obj = MathArticleObject(id=id, name=name, bytes=object_bytes.getvalue())
        item = MathArticleMapping.to_source(obj)

        return item

    def list_names(self) -> list[str]:
        objects = self.client.list_objects(self.bucket_name, recursive=True)

        return [
            object.object_name for object in objects if object.object_name is not None
        ]
