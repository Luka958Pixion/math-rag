from abc import ABC, abstractmethod

from math_rag.core.models import FineTuneJob


class BaseFineTuneJobRunnerService(ABC):
    @abstractmethod
    async def run(self, fine_tune_job: FineTuneJob):
        pass
