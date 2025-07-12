from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionDocument

from .document_indexer import DocumentIndexer


FIELDS = [
    'math_article_id',
    'math_expression_dataset_id',
    'math_expression_group_id',
    'math_expression_index_id',
    'index',
]


class MathExpressionIndexer(DocumentIndexer[MathExpressionDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment, FIELDS)
