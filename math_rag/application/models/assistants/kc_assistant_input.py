from pydantic import BaseModel


class KCAssistantInput(BaseModel):
    katex: str
    error: str
