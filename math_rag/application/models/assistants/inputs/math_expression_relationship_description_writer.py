from math_rag.application.models.assistants.base import BaseAssistantInput


class MathExpressionRelationshipDescriptionWriter(BaseAssistantInput):
    context: str
    source: int
    target: int
