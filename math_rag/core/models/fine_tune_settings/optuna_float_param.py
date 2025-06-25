from pydantic import BaseModel


class OptunaFloatParam(BaseModel):
    name: str
    low: float
    high: float
    step: float
