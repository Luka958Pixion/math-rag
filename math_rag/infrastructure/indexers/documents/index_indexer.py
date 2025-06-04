from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import IndexDocument

from .document_indexer import DocumentIndexer


FIELDS = ['build_stage', 'build_status']


class IndexIndexer(DocumentIndexer[IndexDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment, FIELDS)
