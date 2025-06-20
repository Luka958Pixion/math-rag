from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionDatasetTestResultDocument

from .document_indexer import DocumentIndexer


FIELDS = ['math_expression_dataset_id', 'math_expression_dataset_test_id']


class MathExpressionDatasetTestResultIndexer(
    DocumentIndexer[MathExpressionDatasetTestResultDocument]
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment, FIELDS)
