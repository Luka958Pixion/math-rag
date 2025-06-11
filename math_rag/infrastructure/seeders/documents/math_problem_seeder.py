from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathProblemDocument

from .document_seeder import DocumentSeeder


class MathProblemSeeder(DocumentSeeder[MathProblemDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
