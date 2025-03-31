from datetime import timedelta

from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs.pbs import PBSProJobAlternate
from math_rag.infrastructure.utils import FormatParserUtil


class PBSProJobAlternateMapping(BaseMapping[PBSProJobAlternate, str]):
    @staticmethod
    def to_source(target: str) -> PBSProJobAlternate:
        fields = [field for field in target.strip().split()]

        return PBSProJobAlternate(
            id=fields[0],
            user=fields[1],
            queue=fields[2],
            name=fields[3],
            session_id=None if fields[4] == '--' else fields[4],
            num_chunks=fields[5],
            num_cpus=fields[6],
            requested_mem=FormatParserUtil.parse_memory(fields[7]),
            requested_time=FormatParserUtil.parse_timedelta(fields[8]),
            state=fields[9],
            elapsed_time=None
            if fields[10] == '--'
            else FormatParserUtil.parse_timedelta(fields[10]),
        )

    @staticmethod
    def to_target(source: PBSProJobAlternate) -> str:
        raise NotImplementedError()
