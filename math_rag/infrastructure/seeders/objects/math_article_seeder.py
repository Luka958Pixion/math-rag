from minio import Minio

from math_rag.infrastructure.models.objects import MathArticleObject

from .object_seeder import ObjectSeeder


class MathArticleSeeder(ObjectSeeder[MathArticleObject]):
    def __init__(self, client: Minio):
        super().__init__(client)
