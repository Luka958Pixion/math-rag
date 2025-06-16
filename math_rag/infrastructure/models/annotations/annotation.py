from datetime import datetime

from pydantic import BaseModel

from .result import Result


class Annotation(BaseModel):
    id: int
    completed_by: int
    result: list[Result]
    was_cancelled: bool
    ground_truth: bool
    created_at: datetime
    updated_at: datetime
    draft_created_at: datetime | None = None
    lead_time: float | None = None
    result_count: int
    task: int
    project: int
