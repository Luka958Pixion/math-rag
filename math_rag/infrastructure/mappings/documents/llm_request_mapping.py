from typing import Generic

from math_rag.application.models.inference import LLMRequest
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import LLMRequestDocument

from .llm_conversation_mapping import LLMConversationMapping
from .llm_params_mapping import LLMParamsMapping


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
        )

    @staticmethod
    def to_target(source: LLMRequest[LLMResponseType]) -> LLMRequestDocument:
        return LLMRequestDocument(
            id=source.id,
            conversation=LLMConversationMapping.to_target(source.conversation),
            params=LLMParamsMapping[LLMResponseType].to_target(source.params),
        )
