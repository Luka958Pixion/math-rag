from datetime import timedelta

from pydantic import BaseModel


class PBSProResourceList(BaseModel):
    mem: int
    num_cpus: int
    num_gpus: int
    num_nodes: int
    place: str
    select: str
    wall_time: timedelta
