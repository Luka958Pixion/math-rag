from pydantic import BaseModel


class TrialResult(BaseModel):
    number: int
    metric: str
    score: float
    train_duration: float
    validate_duration: float


class Result(BaseModel):
    trial_results: list[TrialResult]
