from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathArticleChunkDocument

from .document_seeder import DocumentSeeder


class MathArticleChunkSeeder(DocumentSeeder[MathArticleChunkDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
