from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs.pbs import PBSProJobFull


class PBSProJobMapping(BaseMapping[PBSProJobFull, str]):
    @staticmethod
    def to_source(target: str) -> PBSProJobFull:
        fields = ...
        # TODO

        return PBSProJobFull(
            id=fields['job_id'],
            name=fields['job_name'],
            owner=fields['job_owner'],
            state=fields['job_state'],
            queue=fields['queue'],
        )

    @staticmethod
    def to_target(source: PBSProJobFull) -> str:
        raise NotImplementedError()
