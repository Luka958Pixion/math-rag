from math_rag.application.models.inference import LLMConversation
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import LLMConversationDocument

from .llm_message_mapping import LLMMessageMapping


class LLMConversationMapping(BaseMapping[LLMConversation, LLMConversationDocument]):
    @staticmethod
    def to_source(target: LLMConversationDocument) -> LLMConversation:
        return LLMConversation(id=target.id, messages=target.messages)

    @staticmethod
    def to_target(source: LLMConversation) -> LLMConversationDocument:
        return LLMConversationDocument(
            id=source.id,
            messages=[
                LLMMessageMapping.to_target(message) for message in source.messages
            ],
        )
