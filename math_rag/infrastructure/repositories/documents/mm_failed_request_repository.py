from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import BaseMMFailedRequestRepository
from math_rag.application.models.inference import MMFailedRequest
from math_rag.infrastructure.mappings.documents import MMFailedRequestMapping
from math_rag.infrastructure.models.documents import MMFailedRequestDocument

from .document_repository import DocumentRepository


class MMFailedRequestRepository(
    BaseMMFailedRequestRepository,
    DocumentRepository[MMFailedRequest, MMFailedRequestDocument, MMFailedRequestMapping],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
