from abc import ABC, abstractmethod


class BaseTaskTrackerBackgroundService(ABC):
    @abstractmethod
    async def track(self):
        pass

    @abstractmethod
    async def task(self):
        pass

    @abstractmethod
    async def timeout(self) -> float | None:
        pass
