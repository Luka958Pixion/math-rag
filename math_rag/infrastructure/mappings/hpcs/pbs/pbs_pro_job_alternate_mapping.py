from datetime import timedelta

from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs.pbs import PBSProJobAlternate
from math_rag.infrastructure.utils import HPCParserUtil


class PBSProJobAlternateMapping(BaseMapping[PBSProJobAlternate, str]):
    @staticmethod
    def to_source(target: str) -> PBSProJobAlternate:
        fields = [field for field in target.strip().split()]

        return PBSProJobAlternate(
            id=fields[0],
            name=fields[1],
            user=fields[2],
            time=timedelta(seconds=0) if fields[3] == '0' else fields[3],
            state=fields[4],
            queue=fields[5],
            session_id=fields[6],
            num_chunks=fields[7],
            num_cpus=fields[8],
            requested_mem=HPCParserUtil.parse_memory(fields[9]),
            requested_time=timedelta(seconds=0) if fields[10] == '0' else fields[10],
        )

    @staticmethod
    def to_target(source: PBSProJobAlternate) -> str:
        raise NotImplementedError()
