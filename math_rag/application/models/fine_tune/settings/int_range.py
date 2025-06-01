from pydantic import BaseModel


class IntRange(BaseModel):
    low: int
    high: int
    step: int
