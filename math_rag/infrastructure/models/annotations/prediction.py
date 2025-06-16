from datetime import datetime

from pydantic import BaseModel

from .result import Result


class Prediction(BaseModel):
    result: list[Result]
    score: float
    model_version: str
    task: int
    created_at: datetime
    updated_at: datetime
