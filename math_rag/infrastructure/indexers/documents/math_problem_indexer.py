from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathProblemDocument

from .document_indexer import DocumentIndexer


FIELDS = [
    'timestamp',
]


class MathProblemIndexer(DocumentIndexer[MathProblemDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment, FIELDS)
