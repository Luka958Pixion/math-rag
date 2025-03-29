from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs import HPCGPUStatistics
from math_rag.infrastructure.utils import HPCParserUtil


class HPCGPUStatisticsMapping(BaseMapping[HPCGPUStatistics, str]):
    @staticmethod
    def to_source(target: str) -> HPCGPUStatistics:
        fields = target.strip().split('_')

        return HPCGPUStatistics(
            job_id=fields[0],
            node=fields[1],
            gpu=fields[2],
            used_percent=fields[3].removesuffix(' %'),
            mem_used=HPCParserUtil.parse_memory(fields[4].replace(' ', '')),
        )

    @staticmethod
    def to_target(source: HPCGPUStatistics) -> str:
        raise NotImplementedError()
