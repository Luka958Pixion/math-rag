from math_rag.application.models.assistants.base import BaseAssistantOutput


class KatexCorrectorAssistantOutput(BaseAssistantOutput):
    katex: str
