from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import FineTuneJobDocument

from .document_indexer import DocumentIndexer


FIELDS = []


class FineTuneJobIndexer(DocumentIndexer[FineTuneJobDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment, FIELDS)
