from pydantic import BaseModel


class LLMError(BaseModel):
    message: str
    body: object | None
