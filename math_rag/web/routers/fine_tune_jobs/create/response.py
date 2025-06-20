from pydantic import BaseModel

from math_rag.core.models import FineTuneJob, Task


class Response(BaseModel):
    fine_tune_job: FineTuneJob
    task: Task
