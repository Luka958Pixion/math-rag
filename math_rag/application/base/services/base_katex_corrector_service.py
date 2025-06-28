from abc import ABC, abstractmethod


class BaseKatexCorrectorService(ABC):
    @abstractmethod
    async def correct(self, katexes: list[str], *, max_num_retries: int) -> list[str]:
        pass
