from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MMFailedRequestDocument

from .document_seeder import DocumentSeeder


class MMFailedRequestSeeder(DocumentSeeder[MMFailedRequestDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
