from datetime import timedelta

from pydantic import BaseModel


class PBSProResourcesUsed(BaseModel):
    cpu_percent: int
    cpu_time: timedelta
    num_cpus: int
    mem: int
    vmem: int
    walltime: timedelta
