from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs import HPCGPUStatisticsEntry

from .hpc_gpu_statistics_sub_entry_mapping import HPCGPUStatisticsSubEntryMapping


class HPCGPUStatisticsEntryMapping(BaseMapping[HPCGPUStatisticsEntry, str]):
    @staticmethod
    def to_source(target: str) -> HPCGPUStatisticsEntry:
        fields = target.strip().split('_')

        job_id = fields.pop(0)
        sub_entry = HPCGPUStatisticsSubEntryMapping.to_source(fields)

        return HPCGPUStatisticsEntry(job_id=job_id, sub_entry=sub_entry)

    @staticmethod
    def to_target(source: HPCGPUStatisticsEntry) -> str:
        raise NotImplementedError()
