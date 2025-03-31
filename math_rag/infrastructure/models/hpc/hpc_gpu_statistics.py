from pydantic import BaseModel

from .hpc_gpu_statistics_entry import HPCGPUStatisticsEntry


class HPCGPUStatistics(BaseModel):
    entries: list[HPCGPUStatisticsEntry]
