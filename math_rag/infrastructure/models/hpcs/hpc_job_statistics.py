from datetime import timedelta

from pydantic import BaseModel


class HPCJobStatistics(BaseModel):
    job_id: int
    num_cpus: int
    used_percent: float
    mem: int
    used_mem: int
    walltime: timedelta
    used_walltime: timedelta
    exit_code: str
