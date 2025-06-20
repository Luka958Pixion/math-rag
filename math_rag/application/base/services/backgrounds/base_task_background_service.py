from abc import abstractmethod
from uuid import UUID

from .base_background_service import BaseBackgroundService


class BaseTaskBackgroundService(BaseBackgroundService):
    @abstractmethod
    async def task(self, task_model_id: UUID):
        pass

    @abstractmethod
    def task_model_name(self) -> str:
        pass
