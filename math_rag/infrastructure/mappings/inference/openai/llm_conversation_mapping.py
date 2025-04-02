from typing import Any

from math_rag.application.models.inference import LLMConversation
from math_rag.infrastructure.base import BaseMapping

from .llm_message_mapping import LLMMessageMapping


class LLMConversationMapping(BaseMapping[LLMConversation, list[dict[str, Any]]]):
    @staticmethod
    def to_source(target: list[dict[str, Any]]) -> LLMConversation:
        return LLMConversation(
            messages=[LLMMessageMapping.to_source(message) for message in target]
        )

    @staticmethod
    def to_target(source: LLMConversation) -> list[dict[str, Any]]:
        return [LLMMessageMapping.to_target(message) for message in source.messages]
