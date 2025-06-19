from uuid import UUID

from pymongo import AsyncMongoClient, ReturnDocument

from math_rag.application.base.repositories.documents import BaseTaskRepository
from math_rag.core.enums import TaskStatus
from math_rag.core.models import Task
from math_rag.infrastructure.mappings.documents import TaskMapping
from math_rag.infrastructure.models.documents import TaskDocument

from .document_repository import DocumentRepository


class TaskRepository(
    BaseTaskRepository,
    DocumentRepository[Task, TaskDocument, TaskMapping],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)

    async def find_first_pending(self) -> Task | None:
        bson_doc = await self.collection.find_one(
            filter=dict(task_status=TaskStatus.PENDING.value),
            sort=[('created_at', 1)],
        )

        if bson_doc is None:
            return None

        doc = self.target_cls.model_validate(bson_doc)

        return self.mapping_cls.to_source(doc)

    async def update_task_status(self, id: UUID, task_status: TaskStatus) -> Task:
        bson_doc = await self.collection.find_one_and_update(
            filter=dict(_id=id),
            update={'$set': dict(task_status=task_status.value)},
            return_document=ReturnDocument.AFTER,
        )
        doc = self.target_cls.model_validate(bson_doc)

        return self.mapping_cls.to_source(doc)
