from math_rag.application.models.assistants.base import BaseAssistantOutput


class KatexCorrectorRetrier(BaseAssistantOutput):
    katex: str
