from datetime import timedelta

from pydantic import BaseModel

from math_rag.infrastructure.enums.hpc import HPCQueue
from math_rag.infrastructure.enums.hpc.pbs import PBSProJobState


class PBSProJobAlternate(BaseModel):
    id: str
    user: str
    queue: HPCQueue
    name: str
    session_id: str | None
    num_chunks: int
    num_cpus: int
    requested_mem: int
    requested_time: timedelta
    state: PBSProJobState
    elapsed_time: timedelta | None
