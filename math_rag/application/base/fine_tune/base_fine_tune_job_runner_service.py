from abc import ABC, abstractmethod


class BaseFineTuneJobRunnerService(ABC):
    @abstractmethod
    async def run(self):
        pass
