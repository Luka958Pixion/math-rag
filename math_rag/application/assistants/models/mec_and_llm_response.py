from pydantic import BaseModel, Field


class MECAndLLMResponse(BaseModel):
    label: str = Field(alias='class')
