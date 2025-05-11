from math_rag.application.base.assistants import BaseAssistantInput


class KatexCorrectorAssistantInput(BaseAssistantInput):
    katex: str
    error: str
