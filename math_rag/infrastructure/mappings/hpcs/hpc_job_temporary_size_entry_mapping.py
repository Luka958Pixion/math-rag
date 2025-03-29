from pathlib import Path

from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs import HPCJobTemporarySizeEntry
from math_rag.infrastructure.utils import HPCParserUtil


class HPCJobTemporarySizeEntryMapping(BaseMapping[HPCJobTemporarySizeEntry, str]):
    @staticmethod
    def to_source(target: str) -> HPCJobTemporarySizeEntry:
        job_line, data_line = target.strip().splitlines()
        mem_str, path_str = data_line.strip().split(maxsplit=1)

        job_id = int(job_line.split(':')[1].strip())
        mem = HPCParserUtil.parse_memory(mem_str)
        path = Path(path_str)

        return HPCJobTemporarySizeEntry(job_id=job_id, mem=mem, path=path)

    @staticmethod
    def to_target(source: HPCJobTemporarySizeEntry) -> str:
        raise NotImplementedError()
