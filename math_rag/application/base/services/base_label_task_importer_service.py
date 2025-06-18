from abc import ABC, abstractmethod

from math_rag.core.types import LabelTaskType


class BaseLabelTaskImporterService(ABC):
    @abstractmethod
    async def import_tasks(
        self,
        project_id: int | None,
        *,
        project_name: str,
        label_config: str,
        label_instruction: str | None,
        tasks: list[LabelTaskType],
    ) -> int:
        pass
