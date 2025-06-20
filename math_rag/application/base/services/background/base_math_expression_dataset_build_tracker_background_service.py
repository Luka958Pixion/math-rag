from abc import ABC, abstractmethod


class BaseMathExpressionDatasetBuildTrackerBackgroundService(ABC):
    @abstractmethod
    async def track(self):
        pass
