from abc import ABC, abstractmethod


class BaseIndexBuildTrackerService(ABC):
    @abstractmethod
    async def track(self):
        pass
