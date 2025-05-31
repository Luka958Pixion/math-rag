from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionSampleDocument

from .document_seeder import DocumentSeeder


class MathExpressionSampleSeeder(DocumentSeeder[MathExpressionSampleDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
