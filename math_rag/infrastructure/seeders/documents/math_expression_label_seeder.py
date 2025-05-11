from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import (
    MathExpressionLabelDocument,
)

from .document_seeder import DocumentSeeder


class MathExpressionLabelSeeder(DocumentSeeder[MathExpressionLabelDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
