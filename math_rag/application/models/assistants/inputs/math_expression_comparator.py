from math_rag.application.models.assistants.base import BaseAssistantInput


class MathExpressionComparator(BaseAssistantInput):
    katex: str
    context: str
    other_katex: str
    other_context: str
