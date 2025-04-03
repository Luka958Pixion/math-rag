from abc import ABC, abstractmethod
from pathlib import Path
from typing import AsyncGenerator
from uuid import UUID

from math_rag.application.enums import (
    ApptainerBuildStatus,
    ApptainerOverlayCreateStatus,
)


class BaseApptainerClient(ABC):
    @abstractmethod
    async def build_init(self, def_file_path: Path) -> UUID:
        pass

    @abstractmethod
    async def build_status(self, task_id: UUID) -> ApptainerBuildStatus:
        pass

    @abstractmethod
    async def build_result(self, task_id: UUID) -> AsyncGenerator[bytes, None]:
        pass

    @abstractmethod
    async def build(
        self, def_file_path: Path, *, max_retries: int, poll_interval: float
    ) -> AsyncGenerator[bytes, None]:
        pass

    @abstractmethod
    async def overlay_create_init(self, fakeroot: bool, size: int) -> UUID:
        pass

    @abstractmethod
    async def overlay_create_status(
        self, task_id: UUID
    ) -> ApptainerOverlayCreateStatus:
        pass

    @abstractmethod
    async def overlay_create_result(self, task_id: UUID) -> AsyncGenerator[bytes, None]:
        pass

    @abstractmethod
    async def overlay_create(
        self, fakeroot: bool, size: int, *, max_retries: int, poll_interval: float
    ) -> AsyncGenerator[bytes, None]:
        pass
