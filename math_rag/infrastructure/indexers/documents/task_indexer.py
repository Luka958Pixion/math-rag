from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import TaskDocument

from .document_indexer import DocumentIndexer


FIELDS = ['model_id', 'task_status']


class TaskIndexer(DocumentIndexer[TaskDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment, FIELDS)
