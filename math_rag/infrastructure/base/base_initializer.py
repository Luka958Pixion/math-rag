from abc import ABC, abstractmethod


class BaseInitializer(ABC):
    @abstractmethod
    async def initialize(self):
        pass
