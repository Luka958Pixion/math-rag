from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import (
    MathExpressionClassificationDocument,
)

from .document_seeder import DocumentSeeder


class MathExpressionClassificationSeeder(
    DocumentSeeder[MathExpressionClassificationDocument]
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
