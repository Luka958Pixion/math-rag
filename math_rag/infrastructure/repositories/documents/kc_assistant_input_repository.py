from pymongo import AsyncMongoClient

from math_rag.application.models.assistants import KCAssistantInput
from math_rag.infrastructure.mappings.documents import KCAssistantInputMapping
from math_rag.infrastructure.models.documents import KCAssistantInputDocument

from .common_repository import CommonRepository


class KCAssistantInputRepository(
    CommonRepository[
        KCAssistantInput, KCAssistantInputDocument, KCAssistantInputMapping
    ]
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
