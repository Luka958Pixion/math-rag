from math_rag.application.models.assistants.base import BaseAssistantInput


class MathExpressionRelationshipDetector(BaseAssistantInput):
    chunk: str
    source: int
    target: int
