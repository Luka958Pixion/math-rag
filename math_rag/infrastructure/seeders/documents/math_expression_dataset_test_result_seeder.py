from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionDatasetTestResultDocument

from .document_seeder import DocumentSeeder


class MathExpressionDatasetTestResultSeeder(
    DocumentSeeder[MathExpressionDatasetTestResultDocument]
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
