from math_rag.application.base.assistants import BaseAssistantOutput


class KatexCorrectorRetryAssistantOutput(BaseAssistantOutput):
    katex: str
