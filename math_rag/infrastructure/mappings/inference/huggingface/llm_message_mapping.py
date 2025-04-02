from math_rag.application.models.inference import LLMMessage
from math_rag.infrastructure.base import BaseMapping


class LLMMessageMapping(BaseMapping[LLMMessage, dict[str, str]]):
    @staticmethod
    def to_source(target: dict[str, str]) -> LLMMessage:
        return LLMMessage(role=target['role'], content=target['content'])

    @staticmethod
    def to_target(source: LLMMessage) -> dict[str, str]:
        return {'role': source.role, 'content': source.content}
