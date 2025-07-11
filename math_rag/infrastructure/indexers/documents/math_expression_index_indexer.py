from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionIndexDocument

from .document_indexer import DocumentIndexer


FIELDS = ['build_stage']


class MathExpressionIndexIndexer(DocumentIndexer[MathExpressionIndexDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment, FIELDS)
