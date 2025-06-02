from abc import ABC, abstractmethod
from uuid import UUID

from math_rag.core.models import FineTuneJob


class BaseFineTuneJobRunnerService(ABC):
    @abstractmethod
    async def init(self, fine_tune_job: FineTuneJob) -> str:
        pass

    @abstractmethod
    async def result(
        self,
        job_id: str,
        fine_tune_job_id: UUID,
    ) -> dict | None:
        pass

    @abstractmethod
    async def run(self, fine_tune_job: FineTuneJob, *, poll_interval: float) -> dict:
        pass
