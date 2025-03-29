from datetime import timedelta

from pydantic import BaseModel


class HPCCPUStatistics(BaseModel):
    job_id: int
    num_cpus: int
    used_percent: float
    mem: int  # TODO parse
    used_mem: int  # TODO parse
    walltime: timedelta
    used_walltime: timedelta
    exit_code: str
