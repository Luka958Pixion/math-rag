from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionRelationshipDescriptionDocument

from .document_seeder import DocumentSeeder


class MathExpressionRelationshipDescriptionSeeder(
    DocumentSeeder[MathExpressionRelationshipDescriptionDocument]
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
