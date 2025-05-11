from pymongo import AsyncMongoClient

from math_rag.application.models.assistants import KatexCorrectorAssistantInput
from math_rag.infrastructure.mappings.documents import (
    KatexCorrectorAssistantInputMapping,
)
from math_rag.infrastructure.models.documents import (
    KatexCorrectorAssistantInputDocument,
)

from .document_repository import DocumentRepository


class KatexCorrectorAssistantInputRepository(
    DocumentRepository[
        KatexCorrectorAssistantInput,
        KatexCorrectorAssistantInputDocument,
        KatexCorrectorAssistantInputMapping,
    ]
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
