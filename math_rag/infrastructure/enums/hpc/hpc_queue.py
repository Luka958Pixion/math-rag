from enum import Enum, EnumMeta


class HPCQueueMeta(EnumMeta):
    def __call__(cls, value):
        if value in cls._value2member_map_:
            return cls._value2member_map_[value]

        return cls._value2member_map_['unknown']


class HPCQueue(str, Enum, metaclass=HPCQueueMeta):
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

    UNKNOWN = 'unknown'
