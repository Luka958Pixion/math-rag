from pymongo import AsyncMongoClient

from math_rag.application.models.assistants import KCAssistantOutput
from math_rag.infrastructure.models.documents import KCAssistantOutputDocument

from .common_repository import CommonRepository


class KCAssistantOutputRepository(
    CommonRepository[KCAssistantOutputDocument, KCAssistantOutput]
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(
            client=client,
            deployment=deployment,
            document_cls=KCAssistantOutputDocument,
            internal_cls=KCAssistantOutput,
        )
