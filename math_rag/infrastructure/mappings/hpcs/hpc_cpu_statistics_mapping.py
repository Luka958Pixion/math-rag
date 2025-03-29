from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs import HPCCPUStatistics


class HPCCPUStatisticsMapping(BaseMapping[HPCCPUStatistics, str]):
    @staticmethod
    def to_source(target: str) -> HPCCPUStatistics:
        todo = ...

        return HPCCPUStatistics(
            job_id=todo,
            num_cpus=todo,
            used_percent=todo,
            mem=todo,  # TODO parse
            used_mem=todo,  # TODO parse
            walltime=todo,
            used_walltime=todo,
            exit_code=todo,
        )

    @staticmethod
    def to_target(source: HPCCPUStatistics) -> str:
        raise NotImplementedError()
