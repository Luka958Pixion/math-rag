from pymongo import AsyncMongoClient

from math_rag.application.models.assistants import KatexCorrectorAssistantOutput
from math_rag.infrastructure.mappings.documents import (
    KatexCorrectorAssistantOutputMapping,
)
from math_rag.infrastructure.models.documents import (
    KatexCorrectorAssistantOutputDocument,
)

from .document_repository import DocumentRepository


class KatexCorrectorAssistantOutputRepository(
    DocumentRepository[
        KatexCorrectorAssistantOutput,
        KatexCorrectorAssistantOutputDocument,
        KatexCorrectorAssistantOutputMapping,
    ]
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
