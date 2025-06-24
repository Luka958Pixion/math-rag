from math_rag.application.models.assistants.base import BaseAssistantInput


class KatexCorrector(BaseAssistantInput):
    katex: str
    error: str
