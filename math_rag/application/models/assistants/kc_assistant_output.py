from pydantic import BaseModel


class KCAssistantOutput(BaseModel):
    katex: str
