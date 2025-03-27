from abc import ABC, abstractmethod
from pathlib import Path
from typing import AsyncGenerator
from uuid import UUID

from math_rag.application.enums import ApptainerOverlayCreateStatus


class BaseApptainerOverlayCreatorService(ABC):
    @abstractmethod
    async def overlay_create(self, dfakeroot: bool, size: int) -> UUID:
        pass

    @abstractmethod
    async def overlay_create_status(
        self, task_id: UUID
    ) -> ApptainerOverlayCreateStatus:
        pass

    @abstractmethod
    async def overlay_create_result(self, task_id: UUID) -> AsyncGenerator[bytes, None]:
        pass
