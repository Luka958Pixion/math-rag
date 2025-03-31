from datetime import timedelta

from .pbs_pro_job import PBSProJob


class PBSProJobAlternate(PBSProJob):
    session_id: str
    num_chunks: int
    num_cpus: int
    requested_mem: int
    requested_time: timedelta
