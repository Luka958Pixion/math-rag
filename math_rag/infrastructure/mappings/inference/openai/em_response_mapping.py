from math_rag.application.models.inference import EMResponse
from math_rag.infrastructure.base import BaseMapping
from openai.types.create_embedding_response import Embedding


class EMResponseMapping(BaseMapping[EMResponse, Embedding]):
    @staticmethod
    def to_source(target: Embedding, **kwargs) -> EMResponse:
        request_id = kwargs['request_id']

        return EMResponse(request_id=request_id, embedding=target.embedding)

    @staticmethod
    def to_target(source: EMResponse) -> Embedding:
        raise NotImplementedError()
