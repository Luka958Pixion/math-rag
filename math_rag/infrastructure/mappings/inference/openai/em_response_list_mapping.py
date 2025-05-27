from math_rag.application.models.inference import EMResponseList
from math_rag.infrastructure.base import BaseMapping
from openai.types.create_embedding_response import CreateEmbeddingResponse

from .em_response_mapping import EMResponseMapping


class EMResponseListMapping(BaseMapping[EMResponseList, CreateEmbeddingResponse]):
    @staticmethod
    def to_source(target: CreateEmbeddingResponse, **kwargs) -> EMResponseList:
        request_id = kwargs['request_id']

        return EMResponseList(
            request_id=request_id,
            responses=[EMResponseMapping.to_source(embedding) for embedding in target.data],
        )

    @staticmethod
    def to_target(source: EMResponseList) -> CreateEmbeddingResponse:
        raise NotImplementedError()
