from abc import ABC, abstractmethod


class BaseDatasetBuildTrackerBackgroundService(ABC):
    @abstractmethod
    async def track(self):
        pass
