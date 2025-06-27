from abc import ABC, abstractmethod


class BasePBSProResoucesUsedPusherService(ABC):
    @abstractmethod
    async def push(self, job_name: str):
        pass
