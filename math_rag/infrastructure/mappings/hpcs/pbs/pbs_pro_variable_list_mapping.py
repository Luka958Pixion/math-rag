from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs.pbs import PBSProVariableList


class PBSProVariableListMapping(BaseMapping[PBSProVariableList, str]):
    @staticmethod
    def to_source(target: str) -> PBSProVariableList:
        # TODO

        return PBSProVariableList(...)

    @staticmethod
    def to_target(source: PBSProVariableList) -> str:
        raise NotImplementedError()
