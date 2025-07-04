from abc import ABC, abstractmethod
from typing import Generic

from math_rag.application.models.inference import EMRequest, EMResponseList
from math_rag.application.types.embedders import EmbedderInputType, EmbedderOutputType


class BaseEmbedderProtocol(ABC, Generic[EmbedderInputType, EmbedderOutputType]):
    @abstractmethod
    def encode_to_request(self, input: EmbedderInputType) -> EMRequest:
        pass

    @abstractmethod
    def decode_from_response_list(self, response_list: EMResponseList) -> EmbedderOutputType:
        pass
