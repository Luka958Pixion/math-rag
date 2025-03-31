from pydantic import BaseModel


class HPCGPUStatisticsSubEntry(BaseModel):
    node: str
    gpu: str
    used_percent: int
    mem_used: int
