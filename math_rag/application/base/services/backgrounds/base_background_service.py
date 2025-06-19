from abc import ABC, abstractmethod
from uuid import UUID


class BaseBackgroundService(ABC):
    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def task(self, task_model_id: UUID):
        pass
