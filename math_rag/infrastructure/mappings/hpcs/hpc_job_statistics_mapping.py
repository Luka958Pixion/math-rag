from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs import HPCJobStatistics

from .hpc_job_statistics_entry_mapping import HPCJobStatisticsEntryMapping


class HPCJobStatisticsMapping(BaseMapping[HPCJobStatistics, str]):
    @staticmethod
    def to_source(target: str) -> HPCJobStatistics:
        entries_str = target.strip().splitlines()
        entries = [
            HPCJobStatisticsEntryMapping.to_source(entry_str)
            for entry_str in entries_str
        ]

        return HPCJobStatistics(entries=entries)

    @staticmethod
    def to_target(source: HPCJobStatistics) -> str:
        raise NotImplementedError()
