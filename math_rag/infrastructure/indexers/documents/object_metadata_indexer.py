from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import ObjectMetadataDocument

from .document_indexer import DocumentIndexer


FIELDS = [
    'object_name',
    'metadata',
]


class ObjectMetadataIndexer(DocumentIndexer[ObjectMetadataDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment, FIELDS)
