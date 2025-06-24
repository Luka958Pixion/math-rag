from math_rag.application.models.assistants.base import BaseAssistantOutput


class KatexCorrectorRetry(BaseAssistantOutput):
    katex: str
