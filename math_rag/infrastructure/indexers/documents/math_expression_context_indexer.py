from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionContextDocument

from .document_indexer import DocumentIndexer


FIELDS = [
    'math_article_id',
    'math_expression_id',
    'math_expression_index_id',
]


class MathExpressionContextIndexer(DocumentIndexer[MathExpressionContextDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment, FIELDS)
