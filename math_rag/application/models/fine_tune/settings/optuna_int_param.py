from pydantic import BaseModel


class OptunaIntParam(BaseModel):
    name: str
    low: int
    high: int
    step: int
