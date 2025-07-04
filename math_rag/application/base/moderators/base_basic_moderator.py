from abc import ABC, abstractmethod
from typing import Generic

from math_rag.application.types.moderators import ModeratorInputType, ModeratorOutputType


class BaseBasicModerator(ABC, Generic[ModeratorInputType, ModeratorOutputType]):
    @abstractmethod
    async def moderate(self, input: ModeratorInputType) -> ModeratorOutputType | None:
        pass
