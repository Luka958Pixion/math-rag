from pydantic import BaseModel


class LLMLogprob(BaseModel):
    token: str
    value: float
