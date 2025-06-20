from abc import ABC, abstractmethod


class BaseBackgroundService(ABC):
    @abstractmethod
    async def start(self):
        pass
