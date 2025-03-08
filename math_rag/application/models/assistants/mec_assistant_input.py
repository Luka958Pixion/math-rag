from pydantic import BaseModel


class MECAssistantInput(BaseModel):
    latex: str
