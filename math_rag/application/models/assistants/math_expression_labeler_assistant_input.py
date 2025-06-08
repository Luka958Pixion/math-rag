from math_rag.application.models.assistants.base import BaseAssistantInput


class MathExpressionLabelerAssistantInput(BaseAssistantInput):
    latex: str
