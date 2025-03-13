from math_rag.application.base.assistants import BaseAssistantInput


class KCAssistantInput(BaseAssistantInput):
    katex: str
    error: str
