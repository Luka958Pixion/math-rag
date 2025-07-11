from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionRelationshipDocument

from .document_seeder import DocumentSeeder


class MathExpressionRelationshipSeeder(DocumentSeeder[MathExpressionRelationshipDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
