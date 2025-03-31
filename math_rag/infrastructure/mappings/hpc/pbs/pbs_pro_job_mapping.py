from datetime import timedelta

from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpc.pbs import PBSProJob


class PBSProJobMapping(BaseMapping[PBSProJob, str]):
    @staticmethod
    def to_source(target: str) -> PBSProJob:
        fields = [field for field in target.strip().split()]

        return PBSProJob(
            id=fields[0],
            name=fields[1],
            user=fields[2],
            time=timedelta(seconds=0) if fields[3] == '0' else fields[3],
            state=fields[4],
            queue=fields[5],
        )

    @staticmethod
    def to_target(source: PBSProJob) -> str:
        raise NotImplementedError()
