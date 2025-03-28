from enum import Enum


class PBSProQueue(str, Enum):
    """
    https://wiki.srce.hr/spaces/NR/pages/121966239/Redovi+poslova+Supek
    """

    CPU = 'cpu'
    GPU = 'gpu'
    BIGMEM = 'bigmem'
    CPU_TEST = 'cpu-test'
    GPU_TEST = 'gpu-test'
    CPU_SINGLE = 'cpu-single'
    LOGIN_CPU = 'login-cpu'
    LOGIN_GPU = 'login-gpu'
