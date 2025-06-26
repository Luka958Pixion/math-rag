from pydantic import BaseModel

from .hpc_gpu_statistics_sub_entry import HPCGPUStatisticsSubEntry


class HPCGPUStatisticsEntry(BaseModel):
    job_id: int
    sub_entries: list[HPCGPUStatisticsSubEntry]
