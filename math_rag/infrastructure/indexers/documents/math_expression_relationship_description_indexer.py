from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionRelationshipDescriptionDocument

from .document_indexer import DocumentIndexer


FIELDS = [
    'math_expression_index_id',
    'math_expression_relationship_id',
]


class MathExpressionRelationshipDescriptionIndexer(
    DocumentIndexer[MathExpressionRelationshipDescriptionDocument]
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment, FIELDS)
