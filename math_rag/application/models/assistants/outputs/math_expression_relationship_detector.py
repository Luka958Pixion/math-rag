from math_rag.application.models.assistants.base import BaseAssistantOutput


class MathExpressionRelationshipDetector(BaseAssistantOutput):
    relationship_exists: bool
