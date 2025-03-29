from pydantic import BaseModel


class HPCGPUStats(BaseModel):
    job_id: int
    node: str
    gpu: str
    used_percent: int
    mem_used: int  # TODO parse
