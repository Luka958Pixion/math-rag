from math_rag.application.models.assistants.base import BaseAssistantOutput


class MathExpressionDescriptionWriter(BaseAssistantOutput):
    description: str
