from uuid import UUID

from math_rag.application.base.repositories.documents import BaseIndexRepository, BaseTaskRepository
from math_rag.application.base.services import BaseIndexBuilderService
from math_rag.core.models import Index

from .partials import PartialBackgroundService


class IndexBackgroundService(PartialBackgroundService):
    def __init__(
        self,
        index_builder_service: BaseIndexBuilderService,
        index_repository: BaseIndexRepository,
        task_repository: BaseTaskRepository,
    ):
        super().__init__(task_repository)

        self.index_builder_service = index_builder_service
        self.index_repository = index_repository

    async def task(self, task_model_id: UUID):
        index = await self.index_repository.find_one(filter=dict(id=task_model_id))

        if not index:
            raise ValueError()

        await self.index_builder_service.build(index)

    def task_model_name(self) -> str:
        return Index.__name__
