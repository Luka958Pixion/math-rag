from pydantic import BaseModel


class LLMDefaultResponse(BaseModel):
    content: str
