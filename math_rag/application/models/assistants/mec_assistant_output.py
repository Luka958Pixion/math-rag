from pydantic import BaseModel


class MECAssistantOutput(BaseModel):
    label: str
