from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs.pbs import PBSProResourceList


class PBSProResourceListMapping(BaseMapping[PBSProResourceList, str]):
    @staticmethod
    def to_source(target: str) -> PBSProResourceList:
        # TODO

        return PBSProResourceList(...)

    @staticmethod
    def to_target(source: PBSProResourceList) -> str:
        raise NotImplementedError()
