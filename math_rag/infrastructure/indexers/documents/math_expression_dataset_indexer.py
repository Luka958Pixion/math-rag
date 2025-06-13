from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionDatasetDocument

from .document_indexer import DocumentIndexer


FIELDS = ['build_stage', 'build_status', 'build_from_id', 'build_from_stage']


class MathExpressionDatasetIndexer(DocumentIndexer[MathExpressionDatasetDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment, FIELDS)
