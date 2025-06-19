from pydantic import BaseModel

from math_rag.core.models import FineTuneJob, Task


class FineTuneJobCreateResponse(BaseModel):
    fine_tune_job: FineTuneJob
    task: Task
