from datetime import timedelta

from pydantic import BaseModel

from math_rag.infrastructure.enums.hpcs import HPCQueue
from math_rag.infrastructure.enums.hpcs.pbs import PBSProJobState


class PBSProJobSlim(BaseModel):
    id: str
    name: str
    user: str
    time: timedelta
    state: PBSProJobState
    queue: HPCQueue
