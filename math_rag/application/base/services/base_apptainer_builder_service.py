from abc import ABC, abstractmethod
from pathlib import Path
from typing import AsyncGenerator
from uuid import UUID

from math_rag.application.enums import ApptainerBuildStatus


class BaseApptainerBuilderService(ABC):
    @abstractmethod
    async def build(self, def_file_path: Path) -> UUID:
        pass

    @abstractmethod
    async def build_status(self, task_id: UUID) -> ApptainerBuildStatus:
        pass

    @abstractmethod
    async def build_result(self, task_id: UUID) -> AsyncGenerator[bytes, None]:
        pass
