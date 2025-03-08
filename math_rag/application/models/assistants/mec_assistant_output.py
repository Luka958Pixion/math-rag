from pydantic import BaseModel, Field


class MECAssistantOutput(BaseModel):
    label: str = Field(alias='class')
