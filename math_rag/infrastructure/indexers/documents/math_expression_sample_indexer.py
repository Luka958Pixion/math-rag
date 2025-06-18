from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionSampleDocument

from .document_indexer import DocumentIndexer


FIELDS = [
    'math_expression_id',
    'math_expression_dataset_id',
    'label',
]


class MathExpressionSampleIndexer(DocumentIndexer[MathExpressionSampleDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment, FIELDS)
