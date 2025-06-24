from math_rag.application.models.assistants.base import BaseAssistantOutput


class MathExpressionRelationshipDescriptionWriter(BaseAssistantOutput):
    description: str
