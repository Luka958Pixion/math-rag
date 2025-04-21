from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import (
    BaseEMFailedRequestRepository,
)
from math_rag.application.models.inference import EMFailedRequest
from math_rag.infrastructure.mappings.documents import EMFailedRequestMapping
from math_rag.infrastructure.models.documents import EMFailedRequestDocument

from .document_repository import DocumentRepository


class EMFailedRequestRepository(
    BaseEMFailedRequestRepository,
    DocumentRepository[
        EMFailedRequest, EMFailedRequestDocument, EMFailedRequestMapping
    ],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
