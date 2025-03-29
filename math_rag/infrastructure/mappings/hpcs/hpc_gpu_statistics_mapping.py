from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs import HPCGPUStatistics

from .hpc_gpu_statistics_entry_mapping import HPCGPUStatisticsEntryMapping


class HPCGPUStatisticsMapping(BaseMapping[HPCGPUStatistics, str]):
    @staticmethod
    def to_source(target: str) -> HPCGPUStatistics:
        entries = [
            HPCGPUStatisticsEntryMapping.to_source(line)
            for line in target.strip().splitlines()
        ]

        return HPCGPUStatistics(entries=entries)

    @staticmethod
    def to_target(source: HPCGPUStatistics) -> str:
        raise NotImplementedError()
