from math_rag.application.models.assistants.base import BaseAssistantOutput


class MathExpressionComparator(BaseAssistantOutput):
    is_identical: bool
    reason: str
