from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionDatasetTestDocument

from .document_seeder import DocumentSeeder


class MathExpressionDatasetTestSeeder(DocumentSeeder[MathExpressionDatasetTestDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
