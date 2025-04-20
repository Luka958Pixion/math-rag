from math_rag.application.models.inference import EMResponse
from math_rag.infrastructure.base import BaseMapping


class EMResponseMapping(BaseMapping[EMResponse, list[float]]):
    @staticmethod
    def to_source(target: list[float]) -> EMResponse:
        return EMResponse(embedding=target)

    @staticmethod
    def to_target(source: EMResponse) -> list[float]:
        raise NotImplementedError()
