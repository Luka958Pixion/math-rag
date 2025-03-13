from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import (
    BaseLLMFailedRequestRepository,
)
from math_rag.application.models.inference import LLMFailedRequest
from math_rag.infrastructure.mappings.documents import LLMFailedRequestMapping
from math_rag.infrastructure.models.documents import LLMFailedRequestDocument

from .document_repository import DocumentRepository


class LLMFailedRequestRepository(
    BaseLLMFailedRequestRepository,
    DocumentRepository[
        LLMFailedRequest, LLMFailedRequestDocument, LLMFailedRequestMapping
    ],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
