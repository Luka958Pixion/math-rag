from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs.pbs import PBSProJob


class PBSProJobMapping(BaseMapping[PBSProJob, str]):
    @staticmethod
    def to_source(target: str) -> PBSProJob:
        # TODO

        return PBSProJob(...)

    @staticmethod
    def to_target(source: PBSProJob) -> str:
        raise NotImplementedError()
