from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionDescriptionDocument

from .document_seeder import DocumentSeeder


class MathExpressionDescriptionSeeder(DocumentSeeder[MathExpressionDescriptionDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
