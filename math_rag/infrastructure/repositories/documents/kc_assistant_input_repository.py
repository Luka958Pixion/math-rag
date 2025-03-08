from pymongo import AsyncMongoClient

from math_rag.application.models.assistants import KCAssistantInput
from math_rag.infrastructure.models.documents import KCAssistantInputDocument

from .common_repository import CommonRepository


class KCAssistantInputRepository(
    CommonRepository[KCAssistantInputDocument, KCAssistantInput]
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(
            client=client,
            deployment=deployment,
        )
