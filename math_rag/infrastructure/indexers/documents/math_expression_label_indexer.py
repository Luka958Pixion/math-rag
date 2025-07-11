from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import (
    MathExpressionLabelDocument,
)

from .document_indexer import DocumentIndexer


FIELDS = [
    'math_expression_id',
    'math_expression_dataset_id',
    'math_expression_index_id',
    'value',
]


class MathExpressionLabelIndexer(DocumentIndexer[MathExpressionLabelDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment, FIELDS)
