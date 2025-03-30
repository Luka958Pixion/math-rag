from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs.pbs import PBSProJob


class PBSProJobMapping(BaseMapping[PBSProJob, str]):
    @staticmethod
    def to_source(target: str) -> PBSProJob:
        fields = [field for field in target.strip().splitlines()]

        return PBSProJob(
            id=fields[0],
            name=fields[1],
            user=fields[2],
            time=fields[3],
            state=fields[4],
            queue=fields[5],
        )

    @staticmethod
    def to_target(source: PBSProJob) -> str:
        raise NotImplementedError()
