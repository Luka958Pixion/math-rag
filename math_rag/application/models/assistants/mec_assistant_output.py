from pydantic import Field

from math_rag.application.base.assistants import BaseAssistantOutput


class MECAssistantOutput(BaseAssistantOutput):
    label: str = Field(alias='class')
