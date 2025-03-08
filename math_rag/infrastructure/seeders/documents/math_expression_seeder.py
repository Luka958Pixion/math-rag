from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionDocument

from .common_seeder import CommonSeeder


class MathExpressionSeeder(CommonSeeder[MathExpressionDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
