from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionDocument

from .document_seeder import DocumentSeeder


class LLMFailedRequestSeeder(DocumentSeeder[MathExpressionDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
