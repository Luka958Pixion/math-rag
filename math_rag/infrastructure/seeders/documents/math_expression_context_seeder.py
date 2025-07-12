from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionContextDocument

from .document_seeder import DocumentSeeder


class MathExpressionContextSeeder(DocumentSeeder[MathExpressionContextDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
