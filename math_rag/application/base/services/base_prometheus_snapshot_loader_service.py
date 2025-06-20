from abc import ABC, abstractmethod


class BasePrometheusSnapshotLoaderService(ABC):
    @abstractmethod
    async def load(self):
        pass
