from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpc import HPCGPUStatisticsSubEntry
from math_rag.infrastructure.utils import FormatParserUtil


class HPCGPUStatisticsSubEntryMapping(BaseMapping[HPCGPUStatisticsSubEntry, list[str]]):
    @staticmethod
    def to_source(target: list[str]) -> HPCGPUStatisticsSubEntry:
        return HPCGPUStatisticsSubEntry(
            node=target[0],
            gpu=target[1],
            used_percent=target[2].removesuffix(' %'),
            mem_used=FormatParserUtil.parse_memory(target[3].replace(' ', '')),
        )

    @staticmethod
    def to_target(source: HPCGPUStatisticsSubEntry) -> list[str]:
        raise NotImplementedError()
