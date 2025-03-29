from pydantic import BaseModel

from .hpc_job_statistics_entry import HPCJobStatisticsEntry


class HPCJobStatistics(BaseModel):
    entries: list[HPCJobStatisticsEntry]
