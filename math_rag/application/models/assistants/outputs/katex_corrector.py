from math_rag.application.models.assistants.base import BaseAssistantOutput


class KatexCorrector(BaseAssistantOutput):
    katex: str
