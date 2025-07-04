from abc import ABC, abstractmethod
from typing import Generic

from math_rag.application.types.moderators import ModeratorInputType, ModeratorOutputType


class BaseConcurrentModerator(ABC, Generic[ModeratorInputType, ModeratorOutputType]):
    @abstractmethod
    async def concurrent_moderate(
        self,
        inputs: list[ModeratorInputType],
    ) -> list[ModeratorOutputType]:
        pass
