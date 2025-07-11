from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionDescriptionOptDocument

from .document_indexer import DocumentIndexer


FIELDS = [
    'math_expression_id',
    'math_expression_description_id',
    'math_expression_index_id',
]


class MathExpressionDescriptionOptIndexer(DocumentIndexer[MathExpressionDescriptionOptDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment, FIELDS)
