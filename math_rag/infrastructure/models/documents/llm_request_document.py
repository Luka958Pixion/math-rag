from uuid import UUID

from math_rag.infrastructure.base import BaseDocument

from .llm_conversation_document import LLMConversationDocument
from .llm_params_document import LLMParamsDocument
from .llm_router_params_document import LLMRouterParamsDocument


class LLMRequestDocument(BaseDocument):
    id: UUID
    conversation: LLMConversationDocument
    params: LLMParamsDocument
    router_params: LLMRouterParamsDocument | None
