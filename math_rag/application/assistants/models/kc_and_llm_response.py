from pydantic import BaseModel


class KCAndLLMResponse(BaseModel):
    katex: str
