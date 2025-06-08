from math_rag.application.models.assistants.base import BaseAssistantOutput


class KatexCorrectorRetryAssistantOutput(BaseAssistantOutput):
    katex: str
