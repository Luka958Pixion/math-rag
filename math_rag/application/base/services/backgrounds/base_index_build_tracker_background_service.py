from abc import ABC, abstractmethod


class BaseIndexBuildTrackerBackgroundService(ABC):
    @abstractmethod
    async def track(self):
        pass
