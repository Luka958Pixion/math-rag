from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import ObjectMetadataDocument

from .document_seeder import DocumentSeeder


class ObjectMetadataSeeder(DocumentSeeder[ObjectMetadataDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
