from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionGroupDocument

from .document_indexer import DocumentIndexer


FIELDS = [
    'index_id',
]


class MathExpressionGroupIndexer(DocumentIndexer[MathExpressionGroupDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment, FIELDS)
