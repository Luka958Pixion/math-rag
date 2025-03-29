from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs import HPCGPUStatistics


class HPCGPUStatisticsMapping(BaseMapping[HPCGPUStatistics, str]):
    @staticmethod
    def to_source(target: str) -> HPCGPUStatistics:
        todo = ...

        return HPCGPUStatistics(
            job_id=todo,
            node=todo,
            gpu=todo,
            used_percent=todo,
            mem_used=todo,  # TODO parse
        )

    @staticmethod
    def to_target(source: HPCGPUStatistics) -> str:
        raise NotImplementedError()
