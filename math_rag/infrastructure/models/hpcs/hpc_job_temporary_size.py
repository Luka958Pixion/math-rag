from pydantic import BaseModel

from .hpc_job_temporary_size_entry import HPCJobTemporarySizeEntry


class HPCJobTemporarySize(BaseModel):
    entries: list[HPCJobTemporarySizeEntry]
    mem_total: int
