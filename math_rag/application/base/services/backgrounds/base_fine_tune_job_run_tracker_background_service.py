from abc import ABC, abstractmethod


class BaseFineTuneJobRunTrackerBackgroundService(ABC):
    @abstractmethod
    async def track(self):
        pass
