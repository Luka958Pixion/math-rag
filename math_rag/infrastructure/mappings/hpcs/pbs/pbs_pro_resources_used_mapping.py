from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs.pbs import PBSProResourcesUsed


class PBSProResourcesUsedMapping(BaseMapping[PBSProResourcesUsed, str]):
    @staticmethod
    def to_source(target: str) -> PBSProResourcesUsed:
        # TODO

        return PBSProResourcesUsed(...)

    @staticmethod
    def to_target(source: PBSProResourcesUsed) -> str:
        raise NotImplementedError()
