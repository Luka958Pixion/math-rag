from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionRelationshipDocument

from .document_indexer import DocumentIndexer


FIELDS = [
    'math_expression_index_id',
    'math_expression_source_id',
    'math_expression_target_id',
]


class MathExpressionRelationshipIndexer(DocumentIndexer[MathExpressionRelationshipDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment, FIELDS)
