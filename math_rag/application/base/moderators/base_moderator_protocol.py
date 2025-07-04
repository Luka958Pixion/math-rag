from abc import ABC, abstractmethod
from typing import Generic

from math_rag.application.models.inference import MMRequest, MMResponseList
from math_rag.application.types.moderators import ModeratorInputType, ModeratorOutputType


class BaseModeratorProtocol(ABC, Generic[ModeratorInputType, ModeratorOutputType]):
    @abstractmethod
    def encode_to_request(self, input: ModeratorInputType) -> MMRequest:
        pass

    @abstractmethod
    def decode_from_response_list(self, response_list: MMResponseList) -> ModeratorOutputType:
        pass
