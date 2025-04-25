from datetime import timedelta

from pydantic import BaseModel


class TGISettings(BaseModel):
    num_chunks: int
    num_cpus: int
    num_gpus: int
    mem: int
    wall_time: timedelta
