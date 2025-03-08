from pydantic import BaseModel


class KCRetryAssistantInput(BaseModel):
    katex: str
    error: str
