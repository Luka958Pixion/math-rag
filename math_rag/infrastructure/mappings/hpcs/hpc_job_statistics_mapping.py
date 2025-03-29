from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs import HPCJobStatistics
from math_rag.infrastructure.utils import HPCParserUtil


class HPCJobStatisticsMapping(BaseMapping[HPCJobStatistics, str]):
    @staticmethod
    def to_source(target: str) -> HPCJobStatistics:
        fields = target.strip().split()

        return HPCJobStatistics(
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
    def to_target(source: HPCJobStatistics) -> str:
        raise NotImplementedError()
