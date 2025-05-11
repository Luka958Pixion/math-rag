from math_rag.application.base.assistants import BaseAssistantOutput


class KatexCorrectorAssistantOutput(BaseAssistantOutput):
    katex: str
