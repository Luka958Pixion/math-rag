from math_rag.application.models.assistants.base import BaseAssistantInput


class MathExpressionRelationshipDescriptionWriter(BaseAssistantInput):
    chunk: str
    source: int
    target: int
