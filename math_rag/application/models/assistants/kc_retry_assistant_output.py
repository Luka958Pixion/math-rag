from pydantic import BaseModel


class KCRetryAssistantOutput(BaseModel):
    katex: str
