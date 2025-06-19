from abc import ABC, abstractmethod
from typing import Awaitable


class BaseTaskTrackerBackgroundService(ABC):
    @abstractmethod
    async def track(self, awaitable: Awaitable[None], timeout: float | None):
        pass
