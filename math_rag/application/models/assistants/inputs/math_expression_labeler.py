from math_rag.application.models.assistants.base import BaseAssistantInput


class MathExpressionLabeler(BaseAssistantInput):
    katex: str
