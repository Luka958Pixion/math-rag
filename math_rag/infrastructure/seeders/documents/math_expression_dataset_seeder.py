from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionDatasetDocument

from .document_seeder import DocumentSeeder


class MathExpressionDatasetSeeder(DocumentSeeder[MathExpressionDatasetDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
