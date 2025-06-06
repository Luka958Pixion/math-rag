from abc import ABC, abstractmethod
from typing import Generic

from math_rag.application.models.inference import EMRequest, EMResponseList
from math_rag.application.types.embedants import EmbedantInputType, EmbedantOutputType


class BaseEmbedantProtocol(ABC, Generic[EmbedantInputType, EmbedantOutputType]):
    @abstractmethod
    def encode_to_request(self, input: EmbedantInputType) -> EMRequest:
        pass

    @abstractmethod
    def decode_from_response_list(self, response_list: EMResponseList) -> EmbedantOutputType:
        pass
