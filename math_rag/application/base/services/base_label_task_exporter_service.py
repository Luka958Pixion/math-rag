from abc import ABC, abstractmethod

from math_rag.core.types import LabelTaskType


class BaseLabelTaskExporterService(ABC):
    @abstractmethod
    async def export_tasks(
        self, project_id: int, *, label_task_type: type[LabelTaskType]
    ) -> dict[LabelTaskType, str]:
        pass
