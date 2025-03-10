from pydantic import BaseModel


class LLMTextResponse(BaseModel):
    content: str
