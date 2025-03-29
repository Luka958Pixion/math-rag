from datetime import timedelta

from pydantic import BaseModel

from math_rag.infrastructure.enums import (
    HPCQueue,
    PBSProJobState,
)


class PBSProJobSlim(BaseModel):
    id: str
    name: str
    user: str
    time: timedelta
    state: PBSProJobState
    queue: HPCQueue
