from pydantic import BaseModel

from .hpc_queue_live_entry import HPCQueueLiveEntry


class HPCQueueLive(BaseModel):
    entries: list[HPCQueueLiveEntry]
