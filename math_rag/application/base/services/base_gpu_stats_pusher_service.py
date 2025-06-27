from abc import ABC, abstractmethod


class BaseGPUStatsPusherService(ABC):
    @abstractmethod
    async def push(self):
        pass
