from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionDescriptionDocument

from .document_indexer import DocumentIndexer


FIELDS = [
    'math_expression_id',
    'math_expression_index_id',
]


class MathExpressionDescriptionIndexer(DocumentIndexer[MathExpressionDescriptionDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment, FIELDS)
