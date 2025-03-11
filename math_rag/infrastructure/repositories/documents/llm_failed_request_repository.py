from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import (
    BaseLLMFailedRequestRepository,
)
from math_rag.core.models import MathExpression
from math_rag.infrastructure.mappings.documents import LLMFailedRequestMapping
from math_rag.infrastructure.models.documents import LLMFailedRequestDocument

from .document_repository import DocumentRepository


class LLMFailedRequestRepository(
    BaseLLMFailedRequestRepository,
    DocumentRepository[
        MathExpression, LLMFailedRequestDocument, LLMFailedRequestMapping
    ],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
