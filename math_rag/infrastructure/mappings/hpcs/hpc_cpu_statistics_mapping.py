from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs import HPCCPUStatistics
from math_rag.infrastructure.utils import HPCParserUtil


class HPCCPUStatisticsMapping(BaseMapping[HPCCPUStatistics, str]):
    @staticmethod
    def to_source(target: str) -> HPCCPUStatistics:
        fields = target.strip().split()

        return HPCCPUStatistics(
            job_id=fields[0],
            num_cpus=fields[1],
            used_percent=fields[1],
            mem=HPCParserUtil.parse_memory(fields[3]),
            used_mem=HPCParserUtil.parse_memory(fields[4]),
            walltime=fields[5],
            used_walltime=fields[6],
            exit_code=fields[7],
        )

    @staticmethod
    def to_target(source: HPCCPUStatistics) -> str:
        raise NotImplementedError()
