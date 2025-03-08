from pymongo import AsyncMongoClient

from math_rag.application.models.assistants import KCAssistantOutput
from math_rag.infrastructure.mappings.documents import KCAssistantOutputMapping
from math_rag.infrastructure.models.documents import KCAssistantOutputDocument

from .common_repository import CommonRepository


class KCAssistantOutputRepository(
    CommonRepository[
        KCAssistantOutput, KCAssistantOutputDocument, KCAssistantOutputMapping
    ]
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
