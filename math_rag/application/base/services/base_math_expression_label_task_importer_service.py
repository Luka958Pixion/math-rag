from abc import ABC, abstractmethod
from uuid import UUID


class BaseMathExpressionLabelTaskImporterService(ABC):
    @abstractmethod
    async def import_tasks(
        self, project_id: int | None, *, dataset_id: UUID, split_name: str
    ) -> int:
        pass
