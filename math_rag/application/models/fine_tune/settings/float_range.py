from pydantic import BaseModel


class FloatRange(BaseModel):
    low: float
    high: float
    step: float
