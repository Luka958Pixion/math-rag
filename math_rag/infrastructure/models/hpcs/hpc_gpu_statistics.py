from pydantic import BaseModel


class HPCGPUStatistics(BaseModel):
    job_id: int
    node: str
    gpu: str
    used_percent: int
    mem_used: int
