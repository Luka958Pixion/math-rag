from abc import ABC, abstractmethod
from pathlib import Path
from typing import AsyncGenerator


class BaseApptainerService(ABC):
    @abstractmethod
    async def build(
        self, def_file_path: Path, *, max_retries: int, poll_interval: float
    ) -> AsyncGenerator[bytes, None]:
        pass

    @abstractmethod
    async def overlay_create(
        self, fakeroot: bool, size: int, *, max_retries: int, poll_interval: float
    ) -> AsyncGenerator[bytes, None]:
        pass
