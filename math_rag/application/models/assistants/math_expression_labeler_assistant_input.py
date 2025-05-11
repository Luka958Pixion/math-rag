from math_rag.application.base.assistants import BaseAssistantInput


class MathExpressionLabelerAssistantInput(BaseAssistantInput):
    latex: str
