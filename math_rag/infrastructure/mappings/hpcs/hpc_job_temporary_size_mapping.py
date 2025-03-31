from re import fullmatch

from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs import HPCJobTemporarySize
from math_rag.infrastructure.utils import HPCParserUtil

from .hpc_job_temporary_size_entry_mapping import HPCJobTemporarySizeEntryMapping


class HPCJobTemporarySizeMapping(BaseMapping[HPCJobTemporarySize, str]):
    @staticmethod
    def to_source(target: str) -> HPCJobTemporarySize:
        if fullmatch(r'\d+[A-Z]\ttotal', target):
            mem_total_str = target.split()[0]

            entries = []
            mem_total = HPCParserUtil.parse_memory(mem_total_str)

            return HPCJobTemporarySize(entries=entries, mem_total=mem_total)

        entries_str, total_str = target.strip().rsplit('\n', 1)
        mem_total_str = total_str.split()[0]

        entries = [
            HPCJobTemporarySizeEntryMapping.to_source(entry_str)
            for entry_str in entries_str.strip().split('\n\n')
        ]
        mem_total = HPCParserUtil.parse_memory(mem_total_str)

        return HPCJobTemporarySize(entries=entries, mem_total=mem_total)

    @staticmethod
    def to_target(source: HPCJobTemporarySize) -> str:
        raise NotImplementedError()
