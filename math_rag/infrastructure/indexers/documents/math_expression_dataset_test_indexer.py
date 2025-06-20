from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathExpressionDatasetTestDocument

from .document_indexer import DocumentIndexer


FIELDS = [
    'math_expression_dataset_id',
    'math_expression_dataset_split_name',
    'inference_provider',
    'model_provider',
    'model',
]


class MathExpressionDatasetTestIndexer(DocumentIndexer[MathExpressionDatasetTestDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment, FIELDS)
