from pydantic import BaseModel

from math_rag.infrastructure.enums.hpcs import HPCQueue


class HPCQueueLiveEntry(BaseModel):
    queue: HPCQueue
    num_cpus_free: int
    num_cpus_total: int
    num_gpus_free: int
    num_gpus_total: int
    num_nodes_free: int
    num_nodes_total: int
    num_nodes_unavailable: int
    num_nodes_unavailable_total: int
