from pydantic import Field

from math_rag.application.base.assistants import BaseAssistantOutput


class MathExpressionLabelerAssistantOutput(BaseAssistantOutput):
    label: str = Field(..., alias='class')
