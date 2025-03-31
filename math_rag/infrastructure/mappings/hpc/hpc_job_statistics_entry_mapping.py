from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpc import HPCJobStatisticsEntry
from math_rag.infrastructure.utils import FormatParserUtil


class HPCJobStatisticsEntryMapping(BaseMapping[HPCJobStatisticsEntry, str]):
    @staticmethod
    def to_source(target: str) -> HPCJobStatisticsEntry:
        fields = target.strip().split()

        return HPCJobStatisticsEntry(
            job_id=fields[0],
            num_cpus=fields[1],
            used_percent=fields[2],
            mem=FormatParserUtil.parse_memory(fields[3]),
            used_mem=FormatParserUtil.parse_memory(fields[4]),
            walltime=FormatParserUtil.parse_timedelta(fields[5]),
            used_walltime=FormatParserUtil.parse_timedelta(fields[6]),
            exit_code=fields[7],
        )

    @staticmethod
    def to_target(source: HPCJobStatisticsEntry) -> str:
        raise NotImplementedError()
