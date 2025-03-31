from datetime import timedelta

from pydantic import BaseModel

from math_rag.infrastructure.enums.hpc import HPCQueue
from math_rag.infrastructure.enums.hpc.pbs import PBSProJobState


class PBSProJob(BaseModel):
    id: str
    name: str
    user: str
    time: timedelta
    state: PBSProJobState
    queue: HPCQueue
