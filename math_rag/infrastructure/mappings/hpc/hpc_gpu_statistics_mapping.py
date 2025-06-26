from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpc import HPCGPUStatistics, HPCGPUStatisticsEntry

from .hpc_gpu_statistics_sub_entry_mapping import HPCGPUStatisticsSubEntryMapping


class HPCGPUStatisticsMapping(BaseMapping[HPCGPUStatistics, str]):
    @staticmethod
    def to_source(target: str) -> HPCGPUStatistics:
        lines = target.strip().splitlines()

        if not lines:
            return HPCGPUStatistics(entries=[])

        job_id = None
        sub_entries = []
        entries = []

        for line in lines:
            fields = line.strip().split('_')

            if fields[-1] == str():
                sub_entry = HPCGPUStatisticsSubEntryMapping.to_source(fields)
                sub_entries.append(sub_entry)

            else:
                if job_id is not None:
                    entry = HPCGPUStatisticsEntry(job_id=job_id, sub_entries=sub_entries)
                    entries.append(entry)
                    job_id = None
                    sub_entries = []

                job_id = fields.pop(0)
                sub_entry = HPCGPUStatisticsSubEntryMapping.to_source(fields)
                sub_entries.append(sub_entry)

        entry = HPCGPUStatisticsEntry(job_id=job_id, sub_entries=sub_entries)
        entries.append(entry)

        return HPCGPUStatistics(entries=entries)

    @staticmethod
    def to_target(source: HPCGPUStatistics) -> str:
        raise NotImplementedError()
