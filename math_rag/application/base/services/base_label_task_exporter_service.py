from abc import ABC, abstractmethod

from math_rag.core.types import LabelTaskType


class BaseLabelTaskExporterService(ABC):
    @abstractmethod
    async def export_tasks(self, project_id: int) -> list[LabelTaskType]:
        pass
