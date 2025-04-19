from math_rag.application.models.inference import EMResponse
from math_rag.infrastructure.base import BaseMapping
from openai.types.create_embedding_response import Embedding


class EMResponseMapping(BaseMapping[EMResponse, Embedding]):
    @staticmethod
    def to_source(target: Embedding) -> EMResponse:
        return EMResponse(embedding=target.embedding)

    @staticmethod
    def to_target(source: EMResponse) -> Embedding:
        raise NotImplementedError()
