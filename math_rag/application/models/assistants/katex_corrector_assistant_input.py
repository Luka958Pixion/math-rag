from math_rag.application.models.assistants.base import BaseAssistantInput


class KatexCorrectorAssistantInput(BaseAssistantInput):
    katex: str
    error: str
