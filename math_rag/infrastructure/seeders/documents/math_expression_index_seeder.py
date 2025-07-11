from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionIndexDocument

from .document_seeder import DocumentSeeder


class MathExpressionIndexSeeder(DocumentSeeder[MathExpressionIndexDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
