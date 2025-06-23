from typing import Generic

from math_rag.application.models.inference import LLMRequest
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import LLMRequestDocument

from .llm_conversation_mapping import LLMConversationMapping
from .llm_params_mapping import LLMParamsMapping
from .llm_router_params_mapping import LLMRouterParamsMapping


class LLMRequestMapping(
    BaseMapping[LLMRequest[LLMResponseType], LLMRequestDocument],
    Generic[LLMResponseType],
):
    @staticmethod
    def to_source(target: LLMRequestDocument) -> LLMRequest[LLMResponseType]:
        return LLMRequest(
            id=target.id,
            conversation=LLMConversationMapping.to_source(target.conversation),
            params=LLMParamsMapping[LLMResponseType].to_source(target.params),
            router_params=LLMRouterParamsMapping.to_source(target.router_params)
            if target.router_params
            else None,
        )

    @staticmethod
    def to_target(source: LLMRequest[LLMResponseType]) -> LLMRequestDocument:
        return LLMRequestDocument(
            id=source.id,
            conversation=LLMConversationMapping.to_target(source.conversation),
            params=LLMParamsMapping[LLMResponseType].to_target(source.params),
            router_params=LLMRouterParamsMapping.to_target(source.router_params)
            if source.router_params
            else None,
        )
