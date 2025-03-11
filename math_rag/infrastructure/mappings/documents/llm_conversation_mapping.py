from math_rag.application.models.inference import LLMConversation
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import LLMConversationDocument


class LLMConversationMapping(BaseMapping[LLMConversation, LLMConversationDocument]):
    @staticmethod
    def to_source(target: LLMConversationDocument) -> LLMConversation:
        return LLMConversation(id=target._id, messages=target.messages)

    @staticmethod
    def to_target(source: LLMConversation) -> LLMConversationDocument:
        return LLMConversationDocument(_id=source.id, messages=source.messages)
