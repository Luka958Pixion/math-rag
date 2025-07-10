from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionGroupDocument

from .document_seeder import DocumentSeeder


class MathExpressionGroupSeeder(DocumentSeeder[MathExpressionGroupDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
