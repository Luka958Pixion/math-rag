from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs import HPCJobTemporarySize
from math_rag.infrastructure.utils import HPCParserUtil


class HPCJobTemporarySizeMapping(BaseMapping[HPCJobTemporarySize, str]):
    @staticmethod
    def to_source(target: str) -> HPCJobTemporarySize:
        lines = target.strip().splitlines()
        job_id = lines[0].split('JOB_ID : ')[1]
        mem, path = lines[1].split()

        return HPCJobTemporarySize(
            job_id=job_id, mem=HPCParserUtil.parse_memory(mem), path=path
        )

    @staticmethod
    def to_target(source: HPCJobTemporarySize) -> str:
        raise NotImplementedError()
