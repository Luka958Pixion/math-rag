from datetime import timedelta

from pydantic import BaseModel


class HPCJobStatisticsEntry(BaseModel):
    job_id: int
    num_cpus: int
    used_percent: float
    mem: int
    used_mem: int
    wall_time: timedelta
    used_wall_time: timedelta
    exit_code: str
