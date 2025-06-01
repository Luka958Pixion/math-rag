from pydantic import BaseModel


class OptunaSettings(BaseModel):
    study_name: str
    metric_name: str
    direction: str
    n_trials: int
