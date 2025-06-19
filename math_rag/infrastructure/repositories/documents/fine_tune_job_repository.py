from uuid import UUID

from pymongo import AsyncMongoClient, ReturnDocument

from math_rag.application.base.repositories.documents import BaseFineTuneJobRepository
from math_rag.core.enums import TaskStatus
from math_rag.core.models import FineTuneJob
from math_rag.infrastructure.mappings.documents import FineTuneJobMapping
from math_rag.infrastructure.models.documents import FineTuneJobDocument

from .document_repository import DocumentRepository


class FineTuneJobRepository(
    BaseFineTuneJobRepository,
    DocumentRepository[FineTuneJob, FineTuneJobDocument, FineTuneJobMapping],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)

    async def find_first_pending(self) -> FineTuneJob | None:
        bson_doc = await self.collection.find_one(
            filter={'task_status': TaskStatus.PENDING.value},
            sort=[('timestamp', 1)],
        )

        if bson_doc is None:
            return None

        doc = self.target_cls.model_validate(bson_doc)

        return self.mapping_cls.to_source(doc)

    async def update_task_status(self, id: UUID, task_status: TaskStatus) -> FineTuneJob:
        field = 'task_status'

        if field not in self.target_cls.model_fields:
            raise ValueError(f'{self.target_cls.__name__} does not have field {field}')

        bson_doc = await self.collection.find_one_and_update(
            filter={'_id': id},
            update={'$set': {field: task_status.value}},
            return_document=ReturnDocument.AFTER,
        )
        doc = self.target_cls.model_validate(bson_doc)

        return self.mapping_cls.to_source(doc)
