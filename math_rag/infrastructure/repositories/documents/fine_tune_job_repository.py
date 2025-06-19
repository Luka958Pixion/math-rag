from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import BaseFineTuneJobRepository
from math_rag.core.models import FineTuneJob
from math_rag.infrastructure.mappings.documents import FineTuneJobMapping
from math_rag.infrastructure.models.documents import FineTuneJobDocument

from .document_repository import DocumentRepository


class FineTuneJobRepository(
    BaseFineTuneJobRepository,
    DocumentRepository[FineTuneJob, FineTuneJobDocument, FineTuneJobMapping],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
